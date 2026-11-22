"""SCRUM-26 - API de consulta de preco dos ativos (GET /quotes/{ticker}, Yahoo Finance)."""

from datetime import datetime, timedelta
from decimal import Decimal

import httpx
import pytest

from app.modules.quotes.models import Cotacao
from app.shared import yahoo_finance


# ---------- unitarios (leitura da resposta do Yahoo, sem internet) ----------

def responder(monkeypatch, status_code, dados):
    def get_falso(url, **kwargs):
        return httpx.Response(status_code, json=dados, request=httpx.Request("GET", url))
    monkeypatch.setattr(yahoo_finance.httpx, "get", get_falso)


def test_le_o_preco_e_arredonda_para_centavos(monkeypatch):
    responder(monkeypatch, 200, {"chart": {"result": [{"meta": {"regularMarketPrice": 40.889999}}]}})
    assert yahoo_finance.buscar_preco("ITUB4") == Decimal("40.89")


def test_consulta_o_ticker_da_b3_com_sufixo_sa(monkeypatch):
    urls = []

    def get_falso(url, **kwargs):
        urls.append(url)
        return httpx.Response(200, json={"chart": {"result": [{"meta": {"regularMarketPrice": 40.89}}]}},
                              request=httpx.Request("GET", url))
    monkeypatch.setattr(yahoo_finance.httpx, "get", get_falso)
    yahoo_finance.buscar_preco("ITUB4")
    assert urls[0].endswith("/ITUB4.SA")


@pytest.mark.parametrize("status_code, dados", [
    (404, {"chart": {"result": None, "error": {"code": "Not Found"}}}),  # ativo que nao existe no Yahoo
    (200, {"chart": {"result": None}}),                                 # resposta sem preco
    (200, {"chart": {"result": [{"meta": {}}]}}),
])
def test_resposta_sem_preco_gera_erro(monkeypatch, status_code, dados):
    responder(monkeypatch, status_code, dados)
    with pytest.raises(RuntimeError):
        yahoo_finance.buscar_preco("ITUB4")


def test_yahoo_fora_do_ar_gera_erro(monkeypatch):
    def sem_conexao(url, **kwargs):
        raise httpx.ConnectError("sem conexão")
    monkeypatch.setattr(yahoo_finance.httpx, "get", sem_conexao)
    with pytest.raises(RuntimeError):
        yahoo_finance.buscar_preco("ITUB4")


# ---------- API ----------

async def consultar(cliente, cabecalho, ticker):
    return await cliente.get(f"/quotes/{ticker}", headers=cabecalho)


async def test_consulta_o_preco_atual(cliente, banco, investidor_logado, cotacoes_17_11):
    resposta = await consultar(cliente, investidor_logado, "ITUB4")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["ticker"] == "ITUB4"
    assert Decimal(dados["preco"]) == Decimal("40.89")
    assert dados["data_atualizacao"]
    assert banco.get(Cotacao, "ITUB4").preco == Decimal("40.89")  # fica salva no banco


async def test_ticker_em_minusculas(cliente, investidor_logado, cotacoes_17_11):
    resposta = await consultar(cliente, investidor_logado, "itub4")
    assert resposta.status_code == 200
    assert resposta.json()["ticker"] == "ITUB4"


async def test_cotacao_recente_nao_consulta_o_yahoo_de_novo(cliente, investidor_logado, cotacoes_17_11):
    primeira = (await consultar(cliente, investidor_logado, "ITUB4")).json()
    cotacoes_17_11.precos["ITUB4"] = "99.99"
    segunda = (await consultar(cliente, investidor_logado, "ITUB4")).json()
    assert segunda == primeira
    assert cotacoes_17_11.consultas == ["ITUB4"]


async def test_cotacao_com_mais_de_15_minutos_e_atualizada(cliente, banco, investidor_logado, cotacoes_17_11):
    banco.add(Cotacao(ticker="ITUB4", preco=Decimal("30.00"), data_atualizacao=datetime.utcnow() - timedelta(minutes=16)))
    banco.commit()
    resposta = await consultar(cliente, investidor_logado, "ITUB4")
    assert Decimal(resposta.json()["preco"]) == Decimal("40.89")
    banco.expire_all()
    assert banco.get(Cotacao, "ITUB4").preco == Decimal("40.89")


async def test_yahoo_fora_do_ar_devolve_a_ultima_cotacao_salva(cliente, banco, investidor_logado, yahoo):
    ontem = datetime.utcnow() - timedelta(days=1)
    banco.add(Cotacao(ticker="ITUB4", preco=Decimal("40.50"), data_atualizacao=ontem))
    banco.commit()
    resposta = await consultar(cliente, investidor_logado, "ITUB4")
    assert resposta.status_code == 200
    assert Decimal(resposta.json()["preco"]) == Decimal("40.50")
    assert resposta.json()["data_atualizacao"].startswith(ontem.strftime("%Y-%m-%d"))  # mostra a idade do valor


async def test_yahoo_fora_do_ar_sem_cotacao_salva(cliente, investidor_logado, yahoo):
    resposta = await consultar(cliente, investidor_logado, "ITUB4")
    assert resposta.status_code == 503
    assert resposta.json()["detail"] == "Cotação indisponível no momento. Tente novamente mais tarde."


async def test_ativo_fora_do_catalogo_nao_consulta_o_yahoo(cliente, investidor_logado, yahoo):
    resposta = await consultar(cliente, investidor_logado, "ZZZZ9")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Ativo não encontrado."
    assert yahoo.consultas == []


@pytest.mark.parametrize("ticker", ["ITUB-4", "ITUB%204", "ABCDEFGHIJK"])
async def test_ticker_invalido(cliente, investidor_logado, yahoo, ticker):
    resposta = await consultar(cliente, investidor_logado, ticker)
    assert resposta.status_code == 422
    assert yahoo.consultas == []


async def test_sem_login(cliente, banco, yahoo):
    assert (await cliente.get("/quotes/ITUB4")).status_code == 401


async def test_analista_nao_consulta_cotacao(cliente, criar_analista, login, yahoo):
    criar_analista()
    resposta = await consultar(cliente, await login("paulo.ramos", "1234"), "ITUB4")
    assert resposta.status_code == 403
