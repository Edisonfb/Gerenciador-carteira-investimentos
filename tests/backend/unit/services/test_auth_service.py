"""Testes unitarios do servico de autenticacao."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.modules.auth.schemas import LoginEntrada
from app.modules.auth.service import AuthService


class AuthRepositoryFake:
    """Simula buscas por e-mail e nome de usuario sem acessar banco."""

    def __init__(self, usuario):
        self.usuario = usuario

    def buscar_por_email(self, email):
        return self.usuario if email == self.usuario.email else None

    def buscar_por_nome_usuario(self, nome_usuario):
        return self.usuario if nome_usuario == self.usuario.nome_usuario else None


def test_realizar_login_busca_por_email(monkeypatch):
    usuario = SimpleNamespace(
        id_usuario=1,
        email="ana@email.com",
        nome_usuario="ana",
        senha_hash="hash",
        ativo=True,
    )
    service = AuthService(AuthRepositoryFake(usuario))
    monkeypatch.setattr("app.modules.auth.service.verificar_senha", lambda senha, senha_hash: True)
    monkeypatch.setattr("app.modules.auth.service.criar_token_acesso", lambda id_usuario: f"token-{id_usuario}")

    resultado = service.realizar_login("ana@email.com", None, "senha-correta")

    assert resultado == {"access_token": "token-1", "token_type": "bearer"}


def test_realizar_login_busca_por_nome_usuario_quando_email_nao_existe(monkeypatch):
    usuario = SimpleNamespace(
        id_usuario=2,
        email="bia@email.com",
        nome_usuario="bia",
        senha_hash="hash",
        ativo=True,
    )
    service = AuthService(AuthRepositoryFake(usuario))
    monkeypatch.setattr("app.modules.auth.service.verificar_senha", lambda senha, senha_hash: True)
    monkeypatch.setattr("app.modules.auth.service.criar_token_acesso", lambda id_usuario: f"token-{id_usuario}")

    resultado = service.realizar_login(None, "bia", "senha-correta")

    assert resultado == {"access_token": "token-2", "token_type": "bearer"}


def test_login_payload_aceita_email_ou_nome_usuario():
    login_por_email = LoginEntrada.model_validate({"email": "ana@email.com", "senha": "senha"})
    login_por_nome_usuario = LoginEntrada.model_validate({"nome_usuario": "ana", "senha": "senha"})

    assert login_por_email.email == "ana@email.com"
    assert login_por_nome_usuario.nome_usuario == "ana"


def test_login_payload_rejeita_identificador():
    with pytest.raises(ValidationError):
        LoginEntrada.model_validate({"identificador": "ana", "senha": "senha"})
