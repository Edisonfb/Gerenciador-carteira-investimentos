"""Testes e2e do fluxo de gerenciamento de investidores."""


def test_investor_management_flow(auth_client) -> None:
    client, headers = auth_client

    created = client.post(
        "/investors",
        headers=headers,
        json={
            "name": "Investidor E2E",
            "document": "99988877766",
            "email": "inv-e2e@example.com",
        },
    )
    assert created.status_code == 201
    investor_id = created.json()["id"]

    updated = client.put(
        f"/investors/{investor_id}",
        headers=headers,
        json={"name": "Investidor E2E Atualizado"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Investidor E2E Atualizado"

    listed = client.get("/investors", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == investor_id for item in listed.json())
