"""Testes de integracao da API de autenticacao."""


def test_register_login_me_flow(client) -> None:
    register = client.post(
        "/auth/register",
        json={
            "name": "Usuario Teste",
            "email": "teste@example.com",
            "password": "senha123",
        },
    )
    assert register.status_code == 201
    body = register.json()
    assert body["email"] == "teste@example.com"
    assert body["role"] == "analyst"
    assert body["must_change_password"] is False

    login = client.post(
        "/auth/login",
        json={"email": "teste@example.com", "password": "senha123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token

    me = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "teste@example.com"
    assert me.json()["role"] == "analyst"


def test_register_duplicado_retorna_conflito(client) -> None:
    payload = {
        "name": "Usuario Teste",
        "email": "dup@example.com",
        "password": "senha123",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_change_password_flow(client) -> None:
    client.post(
        "/auth/register",
        json={
            "name": "Troca Senha",
            "email": "troca@example.com",
            "password": "senha123",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": "troca@example.com", "password": "senha123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    changed = client.post(
        "/auth/change-password",
        headers=headers,
        json={
            "current_password": "senha123",
            "new_password": "novaSenha1",
        },
    )
    assert changed.status_code == 200
    assert changed.json()["must_change_password"] is False

    old_login = client.post(
        "/auth/login",
        json={"email": "troca@example.com", "password": "senha123"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": "troca@example.com", "password": "novaSenha1"},
    )
    assert new_login.status_code == 200
