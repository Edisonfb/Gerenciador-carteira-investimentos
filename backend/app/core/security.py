"""Funções de segurança para senhas e tokens de sessão."""
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_digitada, senha_hash)


def criar_token_acesso(id_usuario: int) -> str:
    """Gera um JWT assinado que identifica o usuário e expira."""
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def ler_id_usuario_token(token: str) -> int:
    """Valida o JWT e retorna o ID do usuário autenticado."""
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    id_usuario = payload.get("sub")
    if not id_usuario:
        raise jwt.InvalidTokenError("Token sem identificador de usuário.")
    try:
        return int(id_usuario)
    except (TypeError, ValueError) as erro:
        raise jwt.InvalidTokenError("Identificador de usuário inválido.") from erro
