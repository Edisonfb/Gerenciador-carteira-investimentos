"""Links de definição de senha com expiração e invalidação após uso."""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt

from app.core.config import settings
from app.core.security import hash_senha, verificar_senha
from app.shared.email_service import enviar_link_senha


def assinatura_senha(usuario):
    return hmac.new(
        settings.secret_key.encode(), usuario.senha_hash.encode(), hashlib.sha256
    ).hexdigest()


def solicitar_link(repository, email: str, primeiro_acesso: bool):
    usuario = repository.buscar_por_email(email.strip())
    if usuario is None or not usuario.ativo:
        return
    if primeiro_acesso:
        # Contas de investidores recebem uma senha inicial ao serem cadastradas.
        inicial = getattr(usuario, "token_acesso", None)
        if not inicial or not verificar_senha(inicial, usuario.senha_hash):
            return
    agora = datetime.now(timezone.utc)
    token = jwt.encode({
        "sub": str(usuario.id_usuario), "purpose": "password_setup",
        "fingerprint": assinatura_senha(usuario),
        "iat": agora, "exp": agora + timedelta(minutes=30),
    }, settings.secret_key, algorithm="HS256")
    link = settings.endereco_frontend.rstrip("/") + "/definir-senha?" + urlencode({"token": token})
    enviar_link_senha(usuario.email, link, primeiro_acesso)


def validar_primeiro_acesso(repository, email: str, token_inicial: str) -> str:
    usuario = repository.buscar_por_email(email.strip())
    armazenado = getattr(usuario, "token_acesso", None) if usuario else None
    if (usuario is None or not usuario.ativo or not armazenado
        or not hmac.compare_digest(armazenado.encode(), token_inicial.strip().encode())
        or not verificar_senha(armazenado, usuario.senha_hash)):
        raise ValueError("E-mail ou token inválido, ou primeiro acesso já concluído.")
    agora = datetime.now(timezone.utc)
    return jwt.encode({
        "sub": str(usuario.id_usuario), "purpose": "password_setup",
        "fingerprint": assinatura_senha(usuario),
        "iat": agora, "exp": agora + timedelta(minutes=30),
    }, settings.secret_key, algorithm="HS256")


def definir_senha(repository, token: str, senha: str):
    if len(senha) < 8 or len(senha.encode("utf-8")) > 72:
        raise ValueError("A senha deve ter no mínimo 8 caracteres e no máximo 72 bytes.")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"],
                             options={"require": ["sub", "exp", "purpose", "fingerprint"]})
        if payload["purpose"] != "password_setup":
            raise ValueError()
        usuario = repository.buscar_por_id(int(payload["sub"]))
        if usuario is None or not usuario.ativo or not hmac.compare_digest(
            payload["fingerprint"], assinatura_senha(usuario)
        ):
            raise ValueError()
    except (jwt.InvalidTokenError, ValueError, TypeError) as erro:
        raise ValueError("Link inválido ou expirado. Solicite um novo link.") from erro
    usuario.senha_hash = hash_senha(senha)
    if hasattr(usuario, "token_acesso"):
        usuario.token_acesso = ""
    repository.salvar(usuario)
