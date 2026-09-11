"""Acesso a dados do modulo de autenticacao."""

from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.shared.roles import ROLE_ANALYST


class AuthRepository:
    """Operacoes de persistencia de usuarios."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = ROLE_ANALYST,
        must_change_password: bool = False,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            must_change_password=must_change_password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
