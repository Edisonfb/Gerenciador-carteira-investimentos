"""SCRUM-27 - Calcular patrimonio do ativo (quantidade x cotacao atual).

Valores da carteira "Aposentadoria" das US 11.1 e 11.2 (cotacoes de 17/11/2026).
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.investors.models import Investidor
from app.modules.portfolios.calculos import CalculosCarteira
from app.modules.quotes.models import Cotacao


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, 300), ("CRFB3", 0, 0),
    ])


async def resumo(cliente, cabecalho, id_carteira):
    return await cliente.get(f"/portfolios/{id_carteira}/summary", headers=cabecalho)


def ativo(dados, ticker):
    return next(a for a in dados["ativos"] if a["ticker"] == ticker)


# ---------- unitarios ----------

@pytest.mark.parametrize("quantidade, preco, esperado", [
    (100, "15.93", "1593.00"),
    (100, "40.89", "4089.00"),
    (300, "40.89", "12267.00"),
    (0, "40.89", "0.00"),
])
def test_valor_da_posicao_e_quantidade_vezes_cotacao(quantidade, preco, esperado):
    assert CalculosCarteira.valor_posicao(quantidade, Decimal(preco)) == Decimal(esperado)


# ---------- API ----------

async def test_patrimonio_de_cada_ativo(cliente, investidor_logado, aposentadoria):
    resposta = await resumo(cliente, investidor_logado, aposentadoria.id_carteira)
    assert resposta.status_code == 200
    esperado = {"ABEV3": "1593.00", "BBDC4": "1441.00", "EGIE3": "2583.00", "ITUB4": "12267.00"}
    for ticker, valor in esperado.items():
        assert Decimal(ativo(resposta.json(), ticker)["valor_atual"]) == Decimal(valor)
    itub4 = ativo(resposta.json(), "ITUB4")
    assert itub4["quantidade"] == 300
    assert Decimal(itub4["cotacao"]) == Decimal("40.89")


async def test_ativo_sem_quantidade_vale_zero_e_nao_consulta_cotacao(cliente, investidor_logado, aposentadoria, yahoo):
    crfb3 = ativo((await resumo(cliente, investidor_logado, aposentadoria.id_carteira)).json(), "CRFB3")
    assert Decimal(crfb3["valor_atual"]) == 0
    assert crfb3["cotacao"] is None
    assert "CRFB3" not in yahoo.consultas


async def test_cotacao_consultada_fica_salva_no_banco(cliente, banco, investidor_logado, aposentadoria):
    await resumo(cliente, investidor_logado, aposentadoria.id_carteira)
    assert banco.get(Cotacao, "ITUB4").preco == Decimal("40.89")


async def test_cotacao_recente_e_reaproveitada_sem_nova_consulta(cliente, investidor_logado, aposentadoria, yahoo):
    await resumo(cliente, investidor_logado, aposentadoria.id_carteira)
    yahoo.precos["ITUB4"] = "99.99"  # mudou no Yahoo, mas a cotacao salva ainda vale (15 min)
    resposta = await resumo(cliente, investidor_logado, aposentadoria.id_carteira)
    assert Decimal(ativo(resposta.json(), "ITUB4")["valor_atual"]) == Decimal("12267.00")
    assert yahoo.consultas.count("ITUB4") == 1


async def test_cotacao_antiga_e_atualizada(cliente, banco, investidor_logado, aposentadoria):
    banco.add(Cotacao(ticker="ITUB4", preco=Decimal("30.00"), data_atualizacao=datetime.utcnow() - timedelta(hours=1)))
    banco.commit()
    resposta = await resumo(cliente, investidor_logado, aposentadoria.id_carteira)
    assert Decimal(ativo(resposta.json(), "ITUB4")["valor_atual"]) == Decimal("12267.00")


async def test_yahoo_fora_do_ar_usa_a_ultima_cotacao_salva(cliente, banco, investidor_logado, aposentadoria, yahoo):
    for ticker, preco in [("ABEV3", "15.93"), ("BBDC4", "14.41"), ("EGIE3", "25.83"), ("ITUB4", "40.00")]:
        banco.add(Cotacao(ticker=ticker, preco=Decimal(preco), data_atualizacao=datetime.utcnow() - timedelta(days=1)))
    banco.commit()
    yahoo.precos.clear()
    resposta = await resumo(cliente, investidor_logado, aposentadoria.id_carteira)
    assert resposta.status_code == 200
    assert Decimal(ativo(resposta.json(), "ITUB4")["valor_atual"]) == Decimal("12000.00")

