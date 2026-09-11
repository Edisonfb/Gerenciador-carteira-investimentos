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

    def get_by_account_user_id(self, account_user_id: int) -> Investor | None:
        return (
            self.db.query(Investor)
            .filter(Investor.account_user_id == account_user_id)
            .first()
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
        first_name: str,
        last_name: str,
        name: str,
        rg: str,
        document: str,
        email: str,
        phone: str,
        address: str,
        account_user_id: int | None = None,
    ) -> Investor:
        investor = Investor(
            user_id=user_id,
            account_user_id=account_user_id,
            first_name=first_name,
            last_name=last_name,
            name=name,
            rg=rg,
            document=document,
            email=email,
            phone=phone,
            address=address,
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
