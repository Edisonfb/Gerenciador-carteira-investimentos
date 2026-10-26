"""Rotas HTTP do modulo de autenticacao."""

from app.modules.auth.schemas import SolicitarSenhaEntrada, RedefinirSenhaEntrada, PrimeiroAcessoEntrada, PrimeiroAcessoSaida
from app.modules.auth.password_service import solicitar_link, definir_senha, validar_primeiro_acesso
from app.core.config import settings
import logging
import smtplib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.modules.auth.schemas import (
    LoginEntrada,
    LogoutSaida,
    TokenSaida,
    UsuarioSaida,
    UsuarioUpdate,
)

from app.db.session import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService
from app.core.dependencies import obter_usuario_autenticado
from app.modules.auth.models import Usuario

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

@router.post("/logout", response_model=LogoutSaida)
def realizar_logout(
    usuario: Usuario = Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
):
    repository = AuthRepository(db)
    service = AuthService(repository)

    return service.realizar_logout(usuario)

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
def obter_usuario_atual(usuario: Usuario = Depends(obter_usuario_autenticado)):
    return {
        "id_usuario": usuario.id_usuario,
        "email": usuario.email,
        "tipo_usuario": usuario.tipo_usuario.value,
        "ativo": usuario.ativo,
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




def _solicitar_senha(dados, db, primeiro_acesso):
    if not settings.servidor_smtp or not settings.email_remetente:
        raise HTTPException(status_code=503, detail="Envio de e-mail indisponível. Contate o responsável pelo sistema.")
    try:
        solicitar_link(AuthRepository(db), dados.email, primeiro_acesso)
    except (smtplib.SMTPException, OSError):
        # A resposta não revela se o endereço está cadastrado.
        logging.getLogger(__name__).exception("Falha ao enviar link de senha")
    return {"message": "Se houver uma conta ativa elegível, enviaremos as instruções por e-mail."}


@router.post("/esqueci-senha")
def esqueci_senha(dados: SolicitarSenhaEntrada, db: Session = Depends(get_db)):
    return _solicitar_senha(dados, db, False)


@router.post("/primeiro-acesso", response_model=PrimeiroAcessoSaida)
def primeiro_acesso(dados: PrimeiroAcessoEntrada, db: Session = Depends(get_db)):
    try:
        token = validar_primeiro_acesso(AuthRepository(db), dados.email, dados.token)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    return {"token_definicao": token}


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenhaEntrada, db: Session = Depends(get_db)):
    try:
        definir_senha(AuthRepository(db), dados.token, dados.senha)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    return {"message": "Senha definida com sucesso."}
