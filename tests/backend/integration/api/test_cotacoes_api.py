"""Task 26: consulta de preco dos ativos, pelos endpoints HTTP."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.assets.models import Ativo
from app.modules.quotes.models import Cotacao
from app.shared import yahoo_finance


@pytest.fixture
async def investidor_logado(criar_investidor, login):
    criar_investidor()
    return await login("investidor@teste.com")


@pytest.fixture
def ativo(sessao_banco):
    ativo = Ativo(ticker="PETR4", nome="PETROBRAS", setor="Petróleo")
    sessao_banco.add(ativo)
    sessao_banco.commit()
    return ativo


@pytest.fixture
def yahoo(monkeypatch):
    """Substitui o Yahoo Finance e conta quantas vezes ele foi chamado."""
    chamadas = []

    def _configurar(preco=Decimal("38.50"), falhar=False):
        def buscar_preco(ticker):
            chamadas.append(ticker)
            if falhar:
                raise RuntimeError("Yahoo fora do ar")
            return preco
        monkeypatch.setattr(yahoo_finance, "buscar_preco", buscar_preco)
        return chamadas

    return _configurar


async def test_cotacao_exige_token(cliente):
    resposta = await cliente.get("/quotes/PETR4")

    assert resposta.status_code == 401


async def test_busca_cotacao_no_yahoo_e_salva_no_banco(cliente, investidor_logado, ativo, yahoo, sessao_banco):
    chamadas = yahoo(Decimal("38.50"))

    resposta = await cliente.get("/quotes/petr4", headers=investidor_logado)

    assert resposta.status_code == 200
    assert resposta.json()["ticker"] == "PETR4"
    assert Decimal(resposta.json()["preco"]) == Decimal("38.50")
    assert chamadas == ["PETR4"]
    assert sessao_banco.get(Cotacao, "PETR4").preco == Decimal("38.50")


async def test_usa_cotacao_salva_enquanto_esta_valida(cliente, investidor_logado, ativo, yahoo):
    chamadas = yahoo()

    await cliente.get("/quotes/PETR4", headers=investidor_logado)
    await cliente.get("/quotes/PETR4", headers=investidor_logado)

    assert chamadas == ["PETR4"]


async def test_atualiza_cotacao_vencida(cliente, investidor_logado, ativo, yahoo, sessao_banco):
    sessao_banco.add(Cotacao(ticker="PETR4", preco=Decimal("30.00"),
                             data_atualizacao=datetime.utcnow() - timedelta(hours=1)))
    sessao_banco.commit()
    yahoo(Decimal("40.00"))

    resposta = await cliente.get("/quotes/PETR4", headers=investidor_logado)

    assert Decimal(resposta.json()["preco"]) == Decimal("40.00")


async def test_yahoo_fora_do_ar_usa_ultima_cotacao_salva(cliente, investidor_logado, ativo, yahoo, sessao_banco):
    sessao_banco.add(Cotacao(ticker="PETR4", preco=Decimal("30.00"),
                             data_atualizacao=datetime.utcnow() - timedelta(hours=1)))
    sessao_banco.commit()
    yahoo(falhar=True)

    resposta = await cliente.get("/quotes/PETR4", headers=investidor_logado)

    assert resposta.status_code == 200
    assert Decimal(resposta.json()["preco"]) == Decimal("30.00")


async def test_yahoo_fora_do_ar_sem_cotacao_salva_retorna_503(cliente, investidor_logado, ativo, yahoo):
    yahoo(falhar=True)

    resposta = await cliente.get("/quotes/PETR4", headers=investidor_logado)

    assert resposta.status_code == 503


async def test_ativo_fora_do_catalogo_retorna_404_sem_chamar_yahoo(cliente, investidor_logado, yahoo):
    chamadas = yahoo()

    resposta = await cliente.get("/quotes/ZZZZ9", headers=investidor_logado)

    assert resposta.status_code == 404
    assert chamadas == []
