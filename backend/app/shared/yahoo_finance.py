"""Consulta simples de precos de acoes da B3 no Yahoo Finance."""
from decimal import Decimal, InvalidOperation

import httpx


URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA"


class AtivoSemNegociacao(RuntimeError):
    """O Yahoo respondeu, mas nao tem preco do ativo (fora de negociacao)."""


def buscar_preco(ticker: str) -> Decimal:
    """Retorna o ultimo preco negociado do ativo, com duas casas decimais."""
    try:
        resposta = httpx.get(
            URL_YAHOO.format(ticker=ticker),
            params={"interval": "1d", "range": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
    except httpx.HTTPError as erro:
        raise RuntimeError(f"Cotação de {ticker} indisponível no Yahoo Finance.") from erro

    # 404 do Yahoo significa "No data found, symbol may be delisted".
    if resposta.status_code == 404:
        raise AtivoSemNegociacao(f"O ativo {ticker} não está em negociação.")

    try:
        resposta.raise_for_status()
        resultado = resposta.json()["chart"]["result"]
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as erro:
        raise RuntimeError(f"Cotação de {ticker} indisponível no Yahoo Finance.") from erro

    try:
        preco = resultado[0]["meta"]["regularMarketPrice"]
        if preco is None:
            raise TypeError("sem preco")
        return Decimal(str(preco)).quantize(Decimal("0.01"))
    except (KeyError, IndexError, TypeError, ValueError, InvalidOperation) as erro:
        raise AtivoSemNegociacao(f"O ativo {ticker} não está em negociação.") from erro
