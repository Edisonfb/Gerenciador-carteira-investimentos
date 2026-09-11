"""Acesso a dados do modulo de transacoes."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.modules.transactions.models import Transaction


class TransactionRepository:
    """Operacoes de persistencia de transacoes."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_portfolio_ids(self, portfolio_ids: list[int]) -> list[Transaction]:
        if not portfolio_ids:
            return []
        return (
            self.db.query(Transaction)
            .options(joinedload(Transaction.asset))
            .filter(Transaction.portfolio_id.in_(portfolio_ids))
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
            .all()
        )

    def list_by_portfolio(self, portfolio_id: int) -> list[Transaction]:
        return (
            self.db.query(Transaction)
            .options(joinedload(Transaction.asset))
            .filter(Transaction.portfolio_id == portfolio_id)
            .order_by(Transaction.transaction_date.asc(), Transaction.id.asc())
            .all()
        )

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        return (
            self.db.query(Transaction)
            .options(joinedload(Transaction.asset))
            .filter(Transaction.id == transaction_id)
            .first()
        )

    def create(
        self,
        portfolio_id: int,
        asset_id: int | None,
        transaction_type: str,
        quantity: Decimal,
        unit_price: Decimal,
        transaction_date: datetime,
        fees: Decimal,
        notes: str | None,
    ) -> Transaction:
        transaction = Transaction(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            transaction_type=transaction_type,
            quantity=quantity,
            unit_price=unit_price,
            transaction_date=transaction_date,
            fees=fees,
            notes=notes,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction: Transaction) -> None:
        self.db.delete(transaction)
        self.db.commit()

    def get_asset_quantity(self, portfolio_id: int, asset_id: int) -> Decimal:
        transactions = (
            self.db.query(Transaction)
            .filter(
                Transaction.portfolio_id == portfolio_id,
                Transaction.asset_id == asset_id,
            )
            .all()
        )
        total = Decimal("0")
        for tx in transactions:
            if tx.transaction_type == "compra":
                total += Decimal(tx.quantity)
            elif tx.transaction_type == "venda":
                total -= Decimal(tx.quantity)
        return total
