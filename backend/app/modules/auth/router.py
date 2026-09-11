"""Rotas HTTP do modulo de autenticacao."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    """Cadastra um novo usuario."""
    return AuthService(db).register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Autentica usuario com email e senha (JSON)."""
    return AuthService(db).login(payload)


@router.post("/login/form", response_model=TokenResponse, include_in_schema=False)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Autentica usuario no formato OAuth2 (Swagger Authorize)."""
    return AuthService(db).login(
        UserLogin(email=form_data.username, password=form_data.password)
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Retorna os dados do usuario autenticado."""
    return current_user
