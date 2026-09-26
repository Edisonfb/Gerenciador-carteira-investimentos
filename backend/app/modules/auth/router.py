"""Rotas HTTP do modulo de autenticacao."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.modules.auth.schemas import (
    LoginEntrada,
    TokenSaida,
    UsuarioSaida,
    UsuarioUpdate,
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
    if resultado is False:
        raise HTTPException(status_code=403, detail="Usuário inativo. Contate o administrador.")
    if resultado is None:
        raise HTTPException(status_code = 401, detail = "Email ou senha inválidos")
    
    return resultado

@router.get("/usuarios", response_model=list[UsuarioSaida])
def listar_usuarios(db: Session = Depends(get_db)):
    return AuthService(AuthRepository(db)).listar_usuarios()

@router.get("/usuarios/{id_usuario}", response_model=UsuarioSaida)
def get_usuario_por_id(id_usuario: int, db: Session = Depends(get_db)):
    repository = AuthRepository(db)
    service = AuthService(repository)

    usuario = service.get_usuario_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.get("/me", response_model=UsuarioSaida)
def obter_usuario_atual():
    return {
        "id": 1,
        "nome": "Usuario Teste",
        "email": "teste@email.com",
    }

@router.patch("/atualizar/{id_usuario}", response_model=UsuarioUpdate)
def atualizar_usuario(
    id_usuario: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    repository = AuthRepository(db)
    service = AuthService(repository)
    
    usuario = service.atualizar_usuario(id_usuario, dados)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario