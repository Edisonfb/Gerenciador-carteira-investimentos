"""Regras de negocio do modulo de carteiras."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.auth.models import User
from app.modules.investors.repository import InvestorRepository
from app.modules.investors.service import InvestorService
from app.modules.portfolios.models import Portfolio
from app.modules.portfolios.repository import PortfolioRepository
from app.modules.portfolios.schemas import (
    PortfolioCreate,
    PortfolioPositionItem,
    PortfolioSummaryResponse,
    PortfolioUpdate,
)
from app.modules.transactions.repository import TransactionRepository
from app.shared.access import user_can_access_investor


class PortfolioService:
    """Regras de gerenciamento de carteiras."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = PortfolioRepository(db)
        self.investor_repository = InvestorRepository(db)
        self.transaction_repository = TransactionRepository(db)

    def _owned_investor_ids(self, user: User) -> list[int]:
        return [item.id for item in InvestorService(self.db).list_investors(user)]

    def _ensure_portfolio_access(self, user: User, portfolio: Portfolio) -> None:
        investor = self.investor_repository.get_by_id(portfolio.investor_id)
        if investor is None or not user_can_access_investor(user, investor):
            raise ForbiddenError("Carteira nao pertence ao usuario autenticado.")

    def list_portfolios(self, user: User) -> list[Portfolio]:
        return self.repository.list_by_investor_ids(self._owned_investor_ids(user))

    def get_portfolio(self, user: User, portfolio_id: int) -> Portfolio:
        portfolio = self.repository.get_by_id(portfolio_id)
        if portfolio is None:
            raise NotFoundError("Carteira nao encontrada.")
        self._ensure_portfolio_access(user, portfolio)
        return portfolio

    def create_portfolio(self, user: User, data: PortfolioCreate) -> Portfolio:
        investor = self.investor_repository.get_by_id(data.investor_id)
        if investor is None:
            raise NotFoundError("Investidor nao encontrado.")
        if not user_can_access_investor(user, investor):
            raise ForbiddenError("Investidor nao pertence ao usuario autenticado.")
        if not investor.is_active:
            raise ForbiddenError("Investidor inativo.")

        return self.repository.create(
            investor_id=data.investor_id,
            name=data.name.strip(),
            description=data.description,
        )

    def update_portfolio(
        self,
        user: User,
        portfolio_id: int,
        data: PortfolioUpdate,
    ) -> Portfolio:
        portfolio = self.get_portfolio(user, portfolio_id)

        if data.name is not None:
            portfolio.name = data.name.strip()
        if data.description is not None:
            portfolio.description = data.description
        if data.is_active is not None:
            portfolio.is_active = data.is_active

        return self.repository.update(portfolio)

    def delete_portfolio(self, user: User, portfolio_id: int) -> Portfolio:
        portfolio = self.get_portfolio(user, portfolio_id)
        return self.repository.deactivate(portfolio)

    def get_summary(self, user: User, portfolio_id: int) -> PortfolioSummaryResponse:
        portfolio = self.get_portfolio(user, portfolio_id)
        transactions = self.transaction_repository.list_by_portfolio(portfolio.id)

        positions: dict[int, dict] = {}
        total_invested = Decimal("0")
        total_fees = Decimal("0")
        cash_flow = Decimal("0")

        for tx in transactions:
            quantity = Decimal(tx.quantity)
            unit_price = Decimal(tx.unit_price)
            fees = Decimal(tx.fees)
            amount = quantity * unit_price
            total_fees += fees

            if tx.transaction_type == "compra":
                total_invested += amount + fees
                cash_flow -= amount + fees
                if tx.asset_id is not None:
                    position = positions.setdefault(
                        tx.asset_id,
                        {
                            "quantity": Decimal("0"),
                            "total_cost": Decimal("0"),
                            "symbol": tx.asset.symbol if tx.asset else "",
                            "name": tx.asset.name if tx.asset else "",
                        },
                    )
                    position["quantity"] += quantity
                    position["total_cost"] += amount + fees
            elif tx.transaction_type == "venda":
                cash_flow += amount - fees
                if tx.asset_id is not None and tx.asset_id in positions:
                    positions[tx.asset_id]["quantity"] -= quantity
            elif tx.transaction_type == "deposito":
                cash_flow += amount
            elif tx.transaction_type == "retirada":
                cash_flow -= amount + fees
            elif tx.transaction_type == "taxa":
                cash_flow -= fees if fees > 0 else amount
                total_fees += fees if fees > 0 else amount
            elif tx.transaction_type == "rendimento":
                cash_flow += amount

        position_items: list[PortfolioPositionItem] = []
        for asset_id, data in positions.items():
            qty = data["quantity"]
            if qty <= 0:
                continue
            total_cost = data["total_cost"]
            average = (total_cost / qty) if qty > 0 else Decimal("0")
            position_items.append(
                PortfolioPositionItem(
                    asset_id=asset_id,
                    symbol=data["symbol"],
                    name=data["name"],
                    quantity=qty,
                    average_price=average.quantize(Decimal("0.00000001")),
                    total_invested=total_cost.quantize(Decimal("0.00000001")),
                )
            )

        return PortfolioSummaryResponse(
            portfolio_id=portfolio.id,
            portfolio_name=portfolio.name,
            total_invested=total_invested.quantize(Decimal("0.00000001")),
            total_fees=total_fees.quantize(Decimal("0.00000001")),
            cash_flow=cash_flow.quantize(Decimal("0.00000001")),
            positions=position_items,
            transactions_count=len(transactions),
        )
