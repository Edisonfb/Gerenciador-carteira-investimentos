"""Acesso a dados do modulo de carteiras."""

from sqlalchemy.orm import Session

from app.modules.portfolios.models import Portfolio


class PortfolioRepository:
    """Operacoes de persistencia de carteiras."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_investor_ids(self, investor_ids: list[int]) -> list[Portfolio]:
        if not investor_ids:
            return []
        return (
            self.db.query(Portfolio)
            .filter(Portfolio.investor_id.in_(investor_ids))
            .order_by(Portfolio.id.desc())
            .all()
        )

    def get_by_id(self, portfolio_id: int) -> Portfolio | None:
        return self.db.get(Portfolio, portfolio_id)

    def create(
        self,
        investor_id: int,
        name: str,
        description: str | None,
    ) -> Portfolio:
        portfolio = Portfolio(
            investor_id=investor_id,
            name=name,
            description=description,
        )
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def update(self, portfolio: Portfolio) -> Portfolio:
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def deactivate(self, portfolio: Portfolio) -> Portfolio:
        portfolio.is_active = False
        return self.update(portfolio)
