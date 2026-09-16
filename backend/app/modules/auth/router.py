"""Rotas HTTP do modulo de autenticacao."""

from fastapi import APIRouter

from app.modules.auth.schemas import (
    CadastroUsuarioEntrada,
    LoginEntrada,
    TokenSaida,
    UsuarioSaida,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioSaida)
def cadastrar_usuario(dados: CadastroUsuarioEntrada):
    return {
        "id": 1,
        "nome": dados.nome,
        "email": dados.email,
    }


@router.post("/login", response_model=TokenSaida)
def realizar_login(dados: LoginEntrada):
    return {"access_token": "token-falso", "token_type": "bearer"}


@router.get("/me", response_model=UsuarioSaida)
def obter_usuario_atual():
    return {
        "id": 1,
        "nome": "Usuario Teste",
        "email": "teste@email.com",
    }
