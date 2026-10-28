"""Identificacao da sessao e segregacao de perfil (core/dependencies.py).

Cobre a parte de autorizacao do Item 1 (investidor) e do Item 2 (analista):
token ausente/invalido e acesso restrito por tipo de usuario.
"""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import dependencies
from app.core.dependencies import (
    exigir_analista,
    exigir_investidor,
    obter_usuario_autenticado,
)
from app.core.security import criar_token_acesso
from app.db.enums import Tipo_Usuario


def _usuario(tipo, ativo=True, id_usuario=1):
    return SimpleNamespace(id_usuario=id_usuario, tipo_usuario=tipo, ativo=ativo)


def _credenciais(token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.fixture
def usuarios_no_banco(monkeypatch):
    """Substitui o AuthRepository por um dicionario em memoria."""
    usuarios = {}

    class RepositorioFalso:
        def __init__(self, db):
            pass

        def buscar_por_id(self, id_usuario):
            return usuarios.get(id_usuario)

    monkeypatch.setattr(dependencies, "AuthRepository", RepositorioFalso)
    return usuarios


def test_token_valido_retorna_usuario(usuarios_no_banco):
    usuario = _usuario(Tipo_Usuario.INVESTIDOR, id_usuario=7)
    usuarios_no_banco[7] = usuario

    resultado = obter_usuario_autenticado(_credenciais(criar_token_acesso(7)), db=None)

    assert resultado is usuario


def test_sem_token_retorna_401(usuarios_no_banco):
    with pytest.raises(HTTPException) as erro:
        obter_usuario_autenticado(None, db=None)

    assert erro.value.status_code == 401
    assert erro.value.headers == {"WWW-Authenticate": "Bearer"}


def test_token_invalido_retorna_401(usuarios_no_banco):
    with pytest.raises(HTTPException) as erro:
        obter_usuario_autenticado(_credenciais("token-invalido"), db=None)

    assert erro.value.status_code == 401


def test_token_de_usuario_inexistente_retorna_401(usuarios_no_banco):
    with pytest.raises(HTTPException) as erro:
        obter_usuario_autenticado(_credenciais(criar_token_acesso(999)), db=None)

    assert erro.value.status_code == 401


def test_token_de_usuario_inativo_retorna_401(usuarios_no_banco):
    usuarios_no_banco[3] = _usuario(Tipo_Usuario.ANALISTA, ativo=False, id_usuario=3)

    with pytest.raises(HTTPException) as erro:
        obter_usuario_autenticado(_credenciais(criar_token_acesso(3)), db=None)

    assert erro.value.status_code == 401


def test_exigir_investidor_aceita_investidor():
    usuario = _usuario(Tipo_Usuario.INVESTIDOR)

    assert exigir_investidor(usuario) is usuario


def test_exigir_investidor_bloqueia_analista():
    with pytest.raises(HTTPException) as erro:
        exigir_investidor(_usuario(Tipo_Usuario.ANALISTA))

    assert erro.value.status_code == 403


def test_exigir_analista_aceita_analista():
    usuario = _usuario(Tipo_Usuario.ANALISTA)

    assert exigir_analista(usuario) is usuario


def test_exigir_analista_bloqueia_investidor():
    with pytest.raises(HTTPException) as erro:
        exigir_analista(_usuario(Tipo_Usuario.INVESTIDOR))

    assert erro.value.status_code == 403
