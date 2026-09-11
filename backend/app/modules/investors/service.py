"""Regras de negocio do modulo de investidores."""

import secrets
import string

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import hash_password
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.modules.investors.models import Investor
from app.modules.investors.repository import InvestorRepository
from app.modules.investors.schemas import InvestorCreate, InvestorUpdate
from app.shared.access import user_can_access_investor
from app.shared.roles import ROLE_CLIENT, is_analyst, is_client


class InvestorService:
    """Regras de gerenciamento de investidores/clientes."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = InvestorRepository(db)
        self.auth_repository = AuthRepository(db)

    @staticmethod
    def _generate_temporary_password(length: int = 12) -> str:
        """Gera senha temporaria segura para o primeiro acesso do cliente."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def _full_name(first_name: str, last_name: str) -> str:
        return f"{first_name} {last_name}".strip()

    def _require_analyst(self, user: User) -> None:
        if not is_analyst(user.role):
            raise ForbiddenError("Apenas analistas podem gerenciar clientes.")

    def list_investors(self, user: User) -> list[Investor]:
        if is_analyst(user.role):
            return self.repository.list_by_user(user.id)
        if is_client(user.role):
            investor = self.repository.get_by_account_user_id(user.id)
            return [investor] if investor is not None else []
        return []

    def get_investor(self, user: User, investor_id: int) -> Investor:
        investor = self.repository.get_by_id(investor_id)
        if investor is None:
            raise NotFoundError("Investidor nao encontrado.")
        if not user_can_access_investor(user, investor):
            raise ForbiddenError("Investidor nao pertence ao usuario autenticado.")
        return investor

    def create_investor(
        self,
        user: User,
        data: InvestorCreate,
    ) -> tuple[Investor, str]:
        """Pre-cadastra cliente e libera acesso com senha temporaria."""
        self._require_analyst(user)

        document = data.document.strip()
        email = str(data.email).lower()
        first_name = data.first_name.strip()
        last_name = data.last_name.strip()
        full_name = self._full_name(first_name, last_name)

        if self.repository.get_by_document(document) is not None:
            raise ConflictError("Documento ja cadastrado.")
        if self.auth_repository.get_by_email(email) is not None:
            raise ConflictError("Email ja cadastrado.")

        temporary_password = self._generate_temporary_password()
        account_user = self.auth_repository.create(
            name=full_name,
            email=email,
            password_hash=hash_password(temporary_password),
            role=ROLE_CLIENT,
            must_change_password=True,
        )

        try:
            investor = self.repository.create(
                user_id=user.id,
                account_user_id=account_user.id,
                first_name=first_name,
                last_name=last_name,
                name=full_name,
                rg=data.rg.strip(),
                document=document,
                email=email,
                phone=data.phone.strip(),
                address=data.address.strip(),
            )
        except Exception:
            self.auth_repository.delete(account_user)
            raise

        return investor, temporary_password

    def regenerate_access(
        self,
        user: User,
        investor_id: int,
    ) -> tuple[Investor, str]:
        """Reemite senha temporaria do cliente."""
        self._require_analyst(user)
        investor = self.get_investor(user, investor_id)
        if not investor.is_active:
            raise ForbiddenError("Investidor inativo.")
        if investor.account_user_id is None:
            raise NotFoundError("Cliente ainda nao possui conta de acesso.")

        account_user = self.auth_repository.get_by_id(investor.account_user_id)
        if account_user is None:
            raise NotFoundError("Conta de acesso do cliente nao encontrada.")

        temporary_password = self._generate_temporary_password()
        account_user.password_hash = hash_password(temporary_password)
        account_user.must_change_password = True
        self.auth_repository.update(account_user)
        return investor, temporary_password

    def update_investor(
        self,
        user: User,
        investor_id: int,
        data: InvestorUpdate,
    ) -> Investor:
        self._require_analyst(user)
        investor = self.get_investor(user, investor_id)

        if data.document is not None:
            document = data.document.strip()
            existing = self.repository.get_by_document(document)
            if existing is not None and existing.id != investor.id:
                raise ConflictError("Documento ja cadastrado.")
            investor.document = document

        if data.first_name is not None:
            investor.first_name = data.first_name.strip()
        if data.last_name is not None:
            investor.last_name = data.last_name.strip()
        if data.first_name is not None or data.last_name is not None:
            investor.name = self._full_name(investor.first_name, investor.last_name)

        if data.rg is not None:
            investor.rg = data.rg.strip()
        if data.phone is not None:
            investor.phone = data.phone.strip()
        if data.address is not None:
            investor.address = data.address.strip()
        if data.is_active is not None:
            investor.is_active = data.is_active

        if data.email is not None:
            email = str(data.email).lower()
            existing_user = self.auth_repository.get_by_email(email)
            if (
                existing_user is not None
                and existing_user.id != investor.account_user_id
            ):
                raise ConflictError("Email ja cadastrado.")
            investor.email = email
            if investor.account_user_id is not None:
                account_user = self.auth_repository.get_by_id(investor.account_user_id)
                if account_user is not None:
                    account_user.email = email
                    account_user.name = investor.name
                    self.auth_repository.update(account_user)

        return self.repository.update(investor)

    def delete_investor(self, user: User, investor_id: int) -> Investor:
        self._require_analyst(user)
        investor = self.get_investor(user, investor_id)
        return self.repository.deactivate(investor)
