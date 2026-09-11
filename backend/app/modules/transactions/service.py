"""Regras de negocio do modulo de transacoes."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ProjectException
from app.modules.assets.repository import AssetRepository
from app.modules.auth.models import User
from app.modules.investors.repository import InvestorRepository
from app.modules.portfolios.repository import PortfolioRepository
from app.modules.transactions.models import Transaction
from app.modules.transactions.repository import TransactionRepository
from app.modules.transactions.schemas import TransactionCreate, TransactionUpdate
from app.shared.validators import (
    ASSET_REQUIRED_TYPES,
    is_non_negative,
    is_positive_number,
    is_valid_transaction_type,
)


class TransactionService:
    """Regras de gerenciamento de transacoes."""

    def __init__(self, db: Session) -> None:
        self.repository = TransactionRepository(db)
        self.portfolio_repository = PortfolioRepository(db)
        self.investor_repository = InvestorRepository(db)
        self.asset_repository = AssetRepository(db)

    def _owned_portfolio_ids(self, user: User) -> list[int]:
        investor_ids = [
            item.id for item in self.investor_repository.list_by_user(user.id)
        ]
        portfolios = self.portfolio_repository.list_by_investor_ids(investor_ids)
        return [item.id for item in portfolios]

    def _ensure_portfolio_access(self, user: User, portfolio_id: int) -> None:
        portfolio = self.portfolio_repository.get_by_id(portfolio_id)
        if portfolio is None:
            raise NotFoundError("Carteira nao encontrada.")
        investor = self.investor_repository.get_by_id(portfolio.investor_id)
        if investor is None or investor.user_id != user.id:
            raise ForbiddenError("Carteira nao pertence ao usuario autenticado.")
        if not portfolio.is_active:
            raise ForbiddenError("Carteira inativa.")

    def _validate_payload(
        self,
        transaction_type: str,
        asset_id: int | None,
        quantity: Decimal,
        unit_price: Decimal,
        fees: Decimal,
    ) -> str:
        normalized_type = transaction_type.strip().lower()
        if not is_valid_transaction_type(normalized_type):
            raise ProjectException("Tipo de transacao invalido.")

        if not is_non_negative(quantity):
            raise ProjectException("Quantidade nao pode ser negativa.")
        if not is_non_negative(unit_price):
            raise ProjectException("Preco unitario nao pode ser negativo.")
        if not is_non_negative(fees):
            raise ProjectException("Taxas nao podem ser negativas.")

        if normalized_type in ASSET_REQUIRED_TYPES:
            if asset_id is None:
                raise ProjectException(
                    f"Transacao do tipo '{normalized_type}' exige asset_id."
                )
            if not is_positive_number(quantity):
                raise ProjectException("Quantidade deve ser maior que zero.")
            if normalized_type in {"compra", "venda"} and not is_positive_number(
                unit_price
            ):
                raise ProjectException("Preco unitario deve ser maior que zero.")

            asset = self.asset_repository.get_by_id(asset_id)
            if asset is None or not asset.is_active:
                raise NotFoundError("Ativo nao encontrado ou inativo.")

        return normalized_type

    def list_transactions(self, user: User) -> list[Transaction]:
        return self.repository.list_by_portfolio_ids(self._owned_portfolio_ids(user))

    def get_transaction(self, user: User, transaction_id: int) -> Transaction:
        transaction = self.repository.get_by_id(transaction_id)
        if transaction is None:
            raise NotFoundError("Transacao nao encontrada.")
        self._ensure_portfolio_access(user, transaction.portfolio_id)
        return transaction

    def create_transaction(
        self,
        user: User,
        data: TransactionCreate,
    ) -> Transaction:
        self._ensure_portfolio_access(user, data.portfolio_id)
        transaction_type = self._validate_payload(
            data.transaction_type,
            data.asset_id,
            data.quantity,
            data.unit_price,
            data.fees,
        )

        if transaction_type == "venda" and data.asset_id is not None:
            available = self.repository.get_asset_quantity(
                data.portfolio_id,
                data.asset_id,
            )
            if data.quantity > available:
                raise ProjectException(
                    "Quantidade de venda maior do que a disponivel na carteira."
                )

        return self.repository.create(
            portfolio_id=data.portfolio_id,
            asset_id=data.asset_id,
            transaction_type=transaction_type,
            quantity=data.quantity,
            unit_price=data.unit_price,
            transaction_date=data.transaction_date,
            fees=data.fees,
            notes=data.notes,
        )

    def update_transaction(
        self,
        user: User,
        transaction_id: int,
        data: TransactionUpdate,
    ) -> Transaction:
        transaction = self.get_transaction(user, transaction_id)

        transaction_type = data.transaction_type or transaction.transaction_type
        asset_id = data.asset_id if data.asset_id is not None else transaction.asset_id
        quantity = data.quantity if data.quantity is not None else transaction.quantity
        unit_price = (
            data.unit_price if data.unit_price is not None else transaction.unit_price
        )
        fees = data.fees if data.fees is not None else transaction.fees

        # Permite limpar asset_id enviando null apenas via campo explicito no update
        # quando o tipo nao exige ativo; para simplificar, usa o valor atual se omitido.
        if "asset_id" in data.model_fields_set:
            asset_id = data.asset_id

        transaction_type = self._validate_payload(
            transaction_type,
            asset_id,
            Decimal(quantity),
            Decimal(unit_price),
            Decimal(fees),
        )

        if transaction_type == "venda" and asset_id is not None:
            available = self.repository.get_asset_quantity(
                transaction.portfolio_id,
                asset_id,
            )
            # Desconsidera a propria transacao antiga se era venda/compra do mesmo ativo
            if (
                transaction.transaction_type == "venda"
                and transaction.asset_id == asset_id
            ):
                available += Decimal(transaction.quantity)
            elif (
                transaction.transaction_type == "compra"
                and transaction.asset_id == asset_id
            ):
                available -= Decimal(transaction.quantity)

            if Decimal(quantity) > available:
                raise ProjectException(
                    "Quantidade de venda maior do que a disponivel na carteira."
                )

        transaction.transaction_type = transaction_type
        transaction.asset_id = asset_id
        transaction.quantity = quantity
        transaction.unit_price = unit_price
        transaction.fees = fees
        if data.transaction_date is not None:
            transaction.transaction_date = data.transaction_date
        if data.notes is not None:
            transaction.notes = data.notes

        return self.repository.update(transaction)

    def delete_transaction(self, user: User, transaction_id: int) -> None:
        transaction = self.get_transaction(user, transaction_id)
        self.repository.delete(transaction)
