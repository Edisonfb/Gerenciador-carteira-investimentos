"""Funcoes de senha e token usadas na autenticacao (core/security.py)."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    criar_token_acesso,
    hash_senha,
    ler_id_usuario_token,
    verificar_senha,
)


def _token_com_payload(payload: dict, chave: str | None = None) -> str:
    return jwt.encode(payload, chave or settings.secret_key, algorithm="HS256")


def test_hash_nao_guarda_senha_em_texto_puro():
    senha_hash = hash_senha("senha-secreta")

    assert senha_hash != "senha-secreta"
    assert verificar_senha("senha-secreta", senha_hash) is True


def test_verificar_senha_rejeita_senha_errada():
    assert verificar_senha("outra", hash_senha("senha-secreta")) is False


def test_token_gerado_identifica_o_usuario():
    token = criar_token_acesso(42)

    assert ler_id_usuario_token(token) == 42


def test_token_gerado_expira_conforme_configuracao():
    token = criar_token_acesso(1)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

    duracao = payload["exp"] - payload["iat"]
    assert duracao == settings.access_token_expire_minutes * 60


def test_rejeita_token_expirado():
    agora = datetime.now(timezone.utc)
    token = _token_com_payload(
        {"sub": "1", "iat": agora - timedelta(hours=2), "exp": agora - timedelta(hours=1)}
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        ler_id_usuario_token(token)


def test_rejeita_token_assinado_com_outra_chave():
    token = _token_com_payload({"sub": "1"}, chave="outra-chave-com-tamanho-suficiente-hs256")

    with pytest.raises(jwt.InvalidSignatureError):
        ler_id_usuario_token(token)


@pytest.mark.parametrize("payload", [{}, {"sub": ""}, {"sub": "abc"}])
def test_rejeita_token_sem_identificador_valido(payload):
    with pytest.raises(jwt.InvalidTokenError):
        ler_id_usuario_token(_token_com_payload(payload))


def test_rejeita_token_malformado():
    with pytest.raises(jwt.InvalidTokenError):
        ler_id_usuario_token("isto-nao-e-um-jwt")
