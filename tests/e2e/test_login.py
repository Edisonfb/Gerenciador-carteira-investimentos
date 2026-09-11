"""Testes e2e do fluxo de login."""


def test_login_flow(client) -> None:
    register = client.post(
        "/auth/register",
        json={
            "name": "Login E2E",
            "email": "login-e2e@example.com",
            "password": "senha123",
        },
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "login-e2e@example.com", "password": "senha123"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"

    invalid = client.post(
        "/auth/login",
        json={"email": "login-e2e@example.com", "password": "errada"},
    )
    assert invalid.status_code == 401
