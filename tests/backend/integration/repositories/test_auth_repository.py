"""Testes de integracao de repositorios de autenticacao."""

from app.modules.auth.repository import AuthRepository


def test_auth_repository_create_and_get(db) -> None:
    repo = AuthRepository(db)
    user = repo.create(
        name="Repo User",
        email="repo@example.com",
        password_hash="hash",
    )

    assert user.id is not None
    assert repo.get_by_email("repo@example.com") is not None
    assert repo.get_by_id(user.id) is not None
