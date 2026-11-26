"""Ativo fora de negociacao (ex.: CTCA3): o Yahoo nao tem cotacao e a API avisa o usuario.

O Yahoo responde 404 "No data found, symbol may be delisted" para esses ativos.
A tela de transacao, o resumo da carteira e a simulacao de aporte mostram a mensagem.
"""

from datetime import datetime, timedelta
from decimal import Decimal

import httpx
import pytest

from app.modules.assets.models import Ativo
from app.modules.investors.models import Investidor
from app.modules.quotes.models import Cotacao
from app.shared import yahoo_finance


MENSAGEM = "Esse ativo não está em negociação."


@pytest.fixture
def ctca3(banco, yahoo):
    """Cadastra o CTCA3 no catalogo e faz o Yahoo falso responder que ele nao negocia."""
    banco.add(Ativo(ticker="CTCA3", setor="Bens Industriais"))
    banco.commit()
    yahoo.sem_negociacao.add("CTCA3")
    return yahoo


# ---------- unitarios (leitura da resposta do Yahoo, sem internet) ----------

def responder(monkeypatch, status_code, dados):
    def get_falso(url, **kwargs):
        return httpx.Response(status_code, json=dados, request=httpx.Request("GET", url))
    monkeypatch.setattr(yahoo_finance.httpx, "get", get_falso)


@pytest.mark.parametrize("status_code, dados", [
    (404, {"chart": {"result": None, "error": {"code": "Not Found",
                                                "description": "No data found, symbol may be delisted"}}}),
    (200, {"chart": {"result": None}}),
    (200, {"chart": {"result": []}}),
    (200, {"chart": {"result": [{"meta": {}}]}}),
    (200, {"chart": {"result": [{"meta": {"regularMarketPrice": None}}]}}),
])
def test_yahoo_sem_preco_indica_ativo_sem_negociacao(monkeypatch, status_code, dados):
    responder(monkeypatch, status_code, dados)
    with pytest.raises(yahoo_finance.AtivoSemNegociacao):
        yahoo_finance.buscar_preco("CTCA3")


def test_yahoo_com_erro_500_nao_e_ativo_sem_negociacao(monkeypatch):
    responder(monkeypatch, 500, {})
    with pytest.raises(RuntimeError) as erro:
        yahoo_finance.buscar_preco("ITUB4")
    assert not isinstance(erro.value, yahoo_finance.AtivoSemNegociacao)


def test_yahoo_fora_do_ar_nao_e_ativo_sem_negociacao(monkeypatch):
    def sem_conexao(url, **kwargs):
        raise httpx.ConnectError("sem conexão")
    monkeypatch.setattr(yahoo_finance.httpx, "get", sem_conexao)
    with pytest.raises(RuntimeError) as erro:
        yahoo_finance.buscar_preco("ITUB4")
    assert not isinstance(erro.value, yahoo_finance.AtivoSemNegociacao)


# ---------- API: consulta de cotacao (tela de transacao) ----------

async def test_cotacao_de_ativo_sem_negociacao(cliente, investidor_logado, ctca3):
    resposta = await cliente.get("/quotes/CTCA3", headers=investidor_logado)
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == MENSAGEM


async def test_ativo_sem_negociacao_nao_usa_a_cotacao_antiga_do_banco(cliente, banco, investidor_logado, ctca3):
    banco.add(Cotacao(ticker="CTCA3", preco=Decimal("5.00"), data_atualizacao=datetime.utcnow() - timedelta(days=1)))
    banco.commit()
    resposta = await cliente.get("/quotes/CTCA3", headers=investidor_logado)
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == MENSAGEM


async def test_yahoo_fora_do_ar_continua_com_a_mensagem_de_indisponivel(cliente, investidor_logado, yahoo):
    resposta = await cliente.get("/quotes/ITUB4", headers=investidor_logado)
    assert resposta.status_code == 503
    assert resposta.json()["detail"] == "Cotação indisponível no momento. Tente novamente mais tarde."


# ---------- API: resumo e simulacao de aporte da carteira ----------

@pytest.fixture
def carteira_com_ctca3(banco, investidor_logado, criar_carteira, cotacoes_17_11, ctca3):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [("ITUB4", 50, 100), ("CTCA3", 50, 100)])


async def test_resumo_da_carteira_com_ativo_sem_negociacao(cliente, investidor_logado, carteira_com_ctca3):
    resposta = await cliente.get(f"/portfolios/{carteira_com_ctca3.id_carteira}/summary", headers=investidor_logado)
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == (
        "Não foi possível calcular o patrimônio: o ativo CTCA3 não está em negociação."
    )


async def test_simulacao_de_aporte_com_ativo_sem_negociacao(cliente, investidor_logado, carteira_com_ctca3):
    resposta = await cliente.post(
        f"/portfolios/{carteira_com_ctca3.id_carteira}/contribution-simulation",
        json={"aporte": "1000.00"}, headers=investidor_logado,
    )
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == (
        "Não foi possível simular o aporte: o ativo CTCA3 não está em negociação."
    )


async def test_ativo_sem_negociacao_com_quantidade_zero_nao_bloqueia_o_resumo(
    cliente, banco, investidor_logado, criar_carteira, cotacoes_17_11, ctca3,
):
    investidor = banco.query(Investidor).first()
    carteira = criar_carteira(investidor.id_investidor, "Casa", [("ITUB4", 50, 100), ("CTCA3", 50, 0)])
    resposta = await cliente.get(f"/portfolios/{carteira.id_carteira}/summary", headers=investidor_logado)
    assert resposta.status_code == 200
    assert Decimal(resposta.json()["patrimonio_total"]) == Decimal("4089.00")
