"""Testes de integracao da API de investidores."""

from tests.helpers import make_investor_payload


def _auth_header(client) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "name": "Investidor Owner",
            "email": "owner@example.com",
            "password": "senha123",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": "owner@example.com", "password": "senha123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_crud_basico_investidor(client) -> None:
    headers = _auth_header(client)

    created = client.post(
        "/investors",
        headers=headers,
        json=make_investor_payload(
            first_name="Maria",
            last_name="Investidora",
            document="12345678901",
            email="maria@example.com",
        ),
    )
    assert created.status_code == 201
    body = created.json()
    investor_id = body["id"]
    assert body["temporary_password"]
    assert body["account_user_id"] is not None
    assert body["name"] == "Maria Investidora"

    listed = client.get("/investors", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = client.get(f"/investors/{investor_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["document"] == "12345678901"

    deleted = client.delete(f"/investors/{investor_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False


def test_cliente_faz_login_com_senha_temporaria(client) -> None:
    headers = _auth_header(client)
    created = client.post(
        "/investors",
        headers=headers,
        json=make_investor_payload(email="cliente-login@example.com"),
    ).json()

    login = client.post(
        "/auth/login",
        json={
            "email": "cliente-login@example.com",
            "password": created["temporary_password"],
        },
    )
    assert login.status_code == 200
    client_headers = {
        "Authorization": f"Bearer {login.json()['access_token']}",
    }

    me = client.get("/auth/me", headers=client_headers)
    assert me.status_code == 200
    assert me.json()["role"] == "client"
    assert me.json()["must_change_password"] is True

    blocked = client.post(
        "/investors",
        headers=client_headers,
        json=make_investor_payload(
            document="99999999999",
            email="outro@example.com",
        ),
    )
    assert blocked.status_code == 403

    own_list = client.get("/investors", headers=client_headers)
    assert own_list.status_code == 200
    assert len(own_list.json()) == 1
    assert own_list.json()[0]["id"] == created["id"]
