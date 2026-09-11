"""Acesso a dados do modulo de investidores."""

from sqlalchemy.orm import Session

from app.modules.investors.models import Investor


class InvestorRepository:
    """Operacoes de persistencia de investidores."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user(self, user_id: int) -> list[Investor]:
        return (
            self.db.query(Investor)
            .filter(Investor.user_id == user_id)
            .order_by(Investor.id.desc())
            .all()
        )

    def get_by_id(self, investor_id: int) -> Investor | None:
        return self.db.get(Investor, investor_id)

    def get_by_document(self, document: str) -> Investor | None:
        return (
            self.db.query(Investor)
            .filter(Investor.document == document)
            .first()
        )

    def create(
        self,
        user_id: int,
        name: str,
        document: str,
        email: str | None,
    ) -> Investor:
        investor = Investor(
            user_id=user_id,
            name=name,
            document=document,
            email=email,
        )
        self.db.add(investor)
        self.db.commit()
        self.db.refresh(investor)
        return investor

    def update(self, investor: Investor) -> Investor:
        self.db.add(investor)
        self.db.commit()
        self.db.refresh(investor)
        return investor

    def deactivate(self, investor: Investor) -> Investor:
        investor.is_active = False
        return self.update(investor)
