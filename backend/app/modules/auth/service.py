"""Regras de negocio do modulo de autenticacao."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse, UserLogin, UserRegister


class AuthService:
    """Regras de cadastro e autenticacao."""

    def __init__(self, db: Session) -> None:
        self.repository = AuthRepository(db)

    def register(self, data: UserRegister) -> User:
        existing = self.repository.get_by_email(data.email.lower())
        if existing is not None:
            raise ConflictError("Email ja cadastrado.")

        return self.repository.create(
            name=data.name.strip(),
            email=data.email.lower(),
            password_hash=hash_password(data.password),
        )

    def login(self, data: UserLogin) -> TokenResponse:
        user = self.repository.get_by_email(data.email.lower())
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Email ou senha invalidos.")

        token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=token)

    def get_me(self, user: User) -> User:
        return user
