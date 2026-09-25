"""Rotas HTTP do modulo de autenticacao."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.modules.auth.schemas import (
    LoginEntrada,
    TokenSaida,
    UsuarioSaida,
)

from app.db.session import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/login", response_model=TokenSaida)
def realizar_login(dados: LoginEntrada, db: Session = Depends(get_db)):
    repository = AuthRepository(db)
    service = AuthService(repository)

    resultado = service.realizar_login(dados.email, dados.senha)
    if resultado is None:
        raise HTTPException(status_code = 401, detail = "Email ou senha inválidos")
    
    return resultado


@router.get("/me", response_model=UsuarioSaida)
def obter_usuario_atual():
    return {
        "id": 1,
        "nome": "Usuario Teste",
        "email": "teste@email.com",
    }
