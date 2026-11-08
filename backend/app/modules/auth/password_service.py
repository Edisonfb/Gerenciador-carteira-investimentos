"""Links de definição de senha com expiração e invalidação após uso."""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt

from app.core.config import settings
from app.core.security import hash_senha, verificar_senha
from app.db.enums import Tipo_Usuario
from app.shared.email_service import enviar_link_senha


def assinatura_senha(usuario):
    return hmac.new(
        settings.secret_key.encode(), usuario.senha_hash.encode(), hashlib.sha256
    ).hexdigest()


def solicitar_link(repository, email: str, primeiro_acesso: bool):
    """Identifica a conta pelo email principal e envia ao destino de recuperacao."""
    usuario = repository.buscar_por_email(email.strip().lower())
    if usuario is None or not usuario.ativo:
        return
    if getattr(usuario, "tipo_usuario", None) == Tipo_Usuario.INVESTIDOR:
        destinatario = getattr(usuario, "email_recuperacao", None)
        if not destinatario or not destinatario.strip():
            # Nao usa o email principal como alternativa para investidores.
            return
        destinatario = destinatario.strip().lower()
    else:
        # Analistas nao possuem email de recuperacao no modelo atual.
        destinatario = usuario.email
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
    enviar_link_senha(destinatario, link)


def validar_primeiro_acesso(repository, email: str, token_inicial: str) -> str:
    usuario = repository.buscar_por_email(email.strip().lower())
    if (usuario is None or not usuario.ativo
        or getattr(usuario, "tipo_usuario", None) != Tipo_Usuario.INVESTIDOR
        or getattr(usuario, "primeiro_acesso_concluido", True)):
        raise ValueError("E-mail ou token inválido, ou primeiro acesso já concluído.")
    token = token_inicial.strip()
    if not token or len(token.encode("utf-8")) > 72 or not verificar_senha(token, usuario.senha_hash):
        raise ValueError("E-mail ou token inválido, ou primeiro acesso já concluído.")
    agora = datetime.now(timezone.utc)
    return jwt.encode({
        "sub": str(usuario.id_usuario), "purpose": "investor_setup",
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
