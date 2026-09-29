"""Dependências para identificar a sessão autenticada."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import ler_id_usuario_token
from app.db.session import get_db
from app.modules.auth.models import Usuario
from app.modules.auth.repository import AuthRepository


bearer_scheme = HTTPBearer(auto_error=False)


def obter_usuario_autenticado(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    erro_nao_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ausente, inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciais is None:
        raise erro_nao_autorizado

    try:
        id_usuario = ler_id_usuario_token(credenciais.credentials)
    except jwt.InvalidTokenError:
        raise erro_nao_autorizado

    usuario = AuthRepository(db).buscar_por_id(id_usuario)
    if usuario is None or not usuario.ativo:
        raise erro_nao_autorizado
    return usuario


def exigir_investidor(
    usuario: Usuario = Depends(obter_usuario_autenticado),
) -> Usuario:
    if usuario.tipo_usuario.value != "investidor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operação é permitida apenas para investidores.",
        )
    return usuario