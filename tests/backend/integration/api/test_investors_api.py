"""Testes de integracao da API de investidores."""


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
        json={
            "name": "Maria Investidora",
            "document": "12345678901",
            "email": "maria@example.com",
        },
    )
    assert created.status_code == 201
    investor_id = created.json()["id"]

    listed = client.get("/investors", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = client.get(f"/investors/{investor_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["document"] == "12345678901"

    deleted = client.delete(f"/investors/{investor_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["is_active"] is False
