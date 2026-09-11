"""Testes unitarios do AuthService com repositorio mockado."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password
from app.modules.auth.schemas import UserLogin, UserRegister
from app.modules.auth.service import AuthService


def test_register_cria_usuario_quando_email_livre() -> None:
    db = MagicMock()
    service = AuthService(db)
    service.repository = MagicMock()
    service.repository.get_by_email.return_value = None
    service.repository.create.return_value = SimpleNamespace(
        id=1,
        name="Ana",
        email="ana@example.com",
    )

    user = service.register(
        UserRegister(name=" Ana ", email="Ana@Example.com", password="senha123")
    )

    assert user.email == "ana@example.com"
    service.repository.create.assert_called_once()
    kwargs = service.repository.create.call_args.kwargs
    assert kwargs["email"] == "ana@example.com"
    assert kwargs["name"] == "Ana"
    assert kwargs["role"] == "analyst"
    assert kwargs["must_change_password"] is False


def test_register_rejeita_email_duplicado() -> None:
    db = MagicMock()
    service = AuthService(db)
    service.repository = MagicMock()
    service.repository.get_by_email.return_value = SimpleNamespace(id=1)

    with pytest.raises(ConflictError):
        service.register(
            UserRegister(name="Ana", email="ana@example.com", password="senha123")
        )


def test_login_retorna_token_com_credenciais_validas() -> None:
    db = MagicMock()
    service = AuthService(db)
    service.repository = MagicMock()
    service.repository.get_by_email.return_value = SimpleNamespace(
        id=7,
        password_hash=hash_password("senha123"),
    )

    token = service.login(
        UserLogin(email="ana@example.com", password="senha123")
    )

    assert token.access_token
    assert token.token_type == "bearer"


def test_login_rejeita_senha_invalida() -> None:
    db = MagicMock()
    service = AuthService(db)
    service.repository = MagicMock()
    service.repository.get_by_email.return_value = SimpleNamespace(
        id=7,
        password_hash=hash_password("senha123"),
    )

    with pytest.raises(UnauthorizedError):
        service.login(UserLogin(email="ana@example.com", password="errada"))
