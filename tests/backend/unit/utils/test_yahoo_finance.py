"""Leitura da resposta do Yahoo Finance, sem acessar a internet."""
from decimal import Decimal

import httpx
import pytest

from app.shared import yahoo_finance


def responder(monkeypatch, status_code, dados):
    def get_falso(url, **kwargs):
        return httpx.Response(status_code, json=dados, request=httpx.Request("GET", url))
    monkeypatch.setattr(yahoo_finance.httpx, "get", get_falso)


def test_le_o_preco_da_resposta(monkeypatch):
    responder(monkeypatch, 200, {"chart": {"result": [{"meta": {"regularMarketPrice": 47.119998}}]}})

    assert yahoo_finance.buscar_preco("PETR4") == Decimal("47.12")


def test_ativo_inexistente_no_yahoo_gera_erro(monkeypatch):
    responder(monkeypatch, 404, {"chart": {"result": None, "error": {"code": "Not Found"}}})

    with pytest.raises(RuntimeError):
        yahoo_finance.buscar_preco("ZZZZ9")


def test_resposta_sem_preco_gera_erro(monkeypatch):
    responder(monkeypatch, 200, {"chart": {"result": None}})

    with pytest.raises(RuntimeError):
        yahoo_finance.buscar_preco("PETR4")
