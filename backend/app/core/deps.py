"""Dependencias compartilhadas das rotas FastAPI."""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.shared.roles import is_analyst

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessao de banco para uso nas rotas e repositorios."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve o usuario autenticado a partir do Bearer token."""
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = AuthRepository(db).get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_analyst(current_user: User = Depends(get_current_user)) -> User:
    """Garante que o usuario autenticado seja um analista."""
    if not is_analyst(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas analistas podem executar esta operacao.",
        )
    return current_user
