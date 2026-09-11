"""Testes e2e do fluxo de gerenciamento de carteiras."""


def test_portfolio_management_flow(auth_client) -> None:
    client, headers = auth_client

    investor = client.post(
        "/investors",
        headers=headers,
        json={
            "name": "Dono Carteira",
            "document": "11122233344",
            "email": None,
        },
    ).json()

    portfolio = client.post(
        "/portfolios",
        headers=headers,
        json={
            "investor_id": investor["id"],
            "name": "Carteira Principal",
            "description": "E2E",
        },
    )
    assert portfolio.status_code == 201
    portfolio_id = portfolio.json()["id"]

    summary = client.get(f"/portfolios/{portfolio_id}/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["portfolio_id"] == portfolio_id
    assert summary.json()["transactions_count"] == 0
