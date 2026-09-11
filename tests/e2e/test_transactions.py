"""Testes e2e do fluxo de transacoes."""

from tests.helpers import make_investor_payload


def test_transactions_flow(auth_client) -> None:
    client, headers = auth_client

    investor = client.post(
        "/investors",
        headers=headers,
        json=make_investor_payload(
            first_name="Trader",
            last_name="Ops",
            document="55566677788",
            email="trader@example.com",
        ),
    ).json()

    portfolio = client.post(
        "/portfolios",
        headers=headers,
        json={
            "investor_id": investor["id"],
            "name": "Carteira Ops",
            "description": None,
        },
    ).json()

    asset = client.post(
        "/assets",
        headers=headers,
        json={"symbol": "PETR4", "name": "Petrobras", "asset_type": "acao"},
    ).json()

    buy = client.post(
        "/transactions",
        headers=headers,
        json={
            "portfolio_id": portfolio["id"],
            "asset_id": asset["id"],
            "transaction_type": "compra",
            "quantity": "10",
            "unit_price": "30.5",
            "transaction_date": "2026-01-10T10:00:00",
            "fees": "0",
            "notes": "compra e2e",
        },
    )
    assert buy.status_code == 201

    sell_ok = client.post(
        "/transactions",
        headers=headers,
        json={
            "portfolio_id": portfolio["id"],
            "asset_id": asset["id"],
            "transaction_type": "venda",
            "quantity": "4",
            "unit_price": "32",
            "transaction_date": "2026-01-11T10:00:00",
            "fees": "0",
        },
    )
    assert sell_ok.status_code == 201

    sell_invalid = client.post(
        "/transactions",
        headers=headers,
        json={
            "portfolio_id": portfolio["id"],
            "asset_id": asset["id"],
            "transaction_type": "venda",
            "quantity": "20",
            "unit_price": "32",
            "transaction_date": "2026-01-12T10:00:00",
            "fees": "0",
        },
    )
    assert sell_invalid.status_code == 400

    summary = client.get(
        f"/portfolios/{portfolio['id']}/summary",
        headers=headers,
    )
    assert summary.status_code == 200
    assert summary.json()["transactions_count"] == 2
