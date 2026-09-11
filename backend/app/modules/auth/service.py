"""Regras de negocio do modulo de autenticacao."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    PasswordChange,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.shared.roles import ROLE_ANALYST


class AuthService:
    """Regras de cadastro e autenticacao."""

    def __init__(self, db: Session) -> None:
        self.repository = AuthRepository(db)

    def register(self, data: UserRegister) -> User:
        """Cadastra um analista (cadastro publico)."""
        existing = self.repository.get_by_email(data.email.lower())
        if existing is not None:
            raise ConflictError("Email ja cadastrado.")

        return self.repository.create(
            name=data.name.strip(),
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            role=ROLE_ANALYST,
            must_change_password=False,
        )

    def login(self, data: UserLogin) -> TokenResponse:
        user = self.repository.get_by_email(data.email.lower())
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Email ou senha invalidos.")

        token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=token)

    def get_me(self, user: User) -> User:
        return user

    def change_password(self, user: User, data: PasswordChange) -> User:
        """Atualiza a senha e remove a exigencia de troca obrigatoria."""
        if not verify_password(data.current_password, user.password_hash):
            raise UnauthorizedError("Senha atual invalida.")

        user.password_hash = hash_password(data.new_password)
        user.must_change_password = False
        return self.repository.update(user)
