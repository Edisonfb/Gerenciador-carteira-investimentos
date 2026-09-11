"""Regras de negocio do modulo de investidores."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.auth.models import User
from app.modules.investors.models import Investor
from app.modules.investors.repository import InvestorRepository
from app.modules.investors.schemas import InvestorCreate, InvestorUpdate


class InvestorService:
    """Regras de gerenciamento de investidores."""

    def __init__(self, db: Session) -> None:
        self.repository = InvestorRepository(db)

    def list_investors(self, user: User) -> list[Investor]:
        return self.repository.list_by_user(user.id)

    def get_investor(self, user: User, investor_id: int) -> Investor:
        investor = self.repository.get_by_id(investor_id)
        if investor is None:
            raise NotFoundError("Investidor nao encontrado.")
        if investor.user_id != user.id:
            raise ForbiddenError("Investidor nao pertence ao usuario autenticado.")
        return investor

    def create_investor(self, user: User, data: InvestorCreate) -> Investor:
        document = data.document.strip()
        existing = self.repository.get_by_document(document)
        if existing is not None:
            raise ConflictError("Documento ja cadastrado.")

        return self.repository.create(
            user_id=user.id,
            name=data.name.strip(),
            document=document,
            email=str(data.email).lower() if data.email else None,
        )

    def update_investor(
        self,
        user: User,
        investor_id: int,
        data: InvestorUpdate,
    ) -> Investor:
        investor = self.get_investor(user, investor_id)

        if data.document is not None:
            document = data.document.strip()
            existing = self.repository.get_by_document(document)
            if existing is not None and existing.id != investor.id:
                raise ConflictError("Documento ja cadastrado.")
            investor.document = document

        if data.name is not None:
            investor.name = data.name.strip()
        if data.email is not None:
            investor.email = str(data.email).lower()
        if data.is_active is not None:
            investor.is_active = data.is_active

        return self.repository.update(investor)

    def delete_investor(self, user: User, investor_id: int) -> Investor:
        investor = self.get_investor(user, investor_id)
        return self.repository.deactivate(investor)
