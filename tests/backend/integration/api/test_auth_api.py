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
    assert register.json()["email"] == "teste@example.com"

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


def test_register_duplicado_retorna_conflito(client) -> None:
    payload = {
        "name": "Usuario Teste",
        "email": "dup@example.com",
        "password": "senha123",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409
