"""Consulta simples de precos de acoes da B3 no Yahoo Finance."""
from decimal import Decimal, InvalidOperation

import httpx


URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA"


def buscar_preco(ticker: str) -> Decimal:
    """Retorna o ultimo preco negociado do ativo, com duas casas decimais."""
    try:
        resposta = httpx.get(
            URL_YAHOO.format(ticker=ticker),
            params={"interval": "1d", "range": "1d"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        resposta.raise_for_status()
        preco = resposta.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return Decimal(str(preco)).quantize(Decimal("0.01"))
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, InvalidOperation) as erro:
        raise RuntimeError(f"Cotação de {ticker} indisponível no Yahoo Finance.") from erro
