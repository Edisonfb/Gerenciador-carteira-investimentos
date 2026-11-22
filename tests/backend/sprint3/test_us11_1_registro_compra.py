"""US 11.1 - Registro de compra (SCRUM-64 e SCRUM-32)."""

from decimal import Decimal

import pytest

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.transactions.models import Transacao

DATA_17_11 = "2026-11-17T20:29:00-03:00"


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    """Patrimonio total de R$ 9.706,00, com ITUB4 (100 acoes, objetivo 10%)."""
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, 100),
    ])


def quantidade(banco, id_carteira, ticker):
    banco.expire_all()
    return banco.query(AtivoCarteira).filter_by(id_carteira=id_carteira, ticker=ticker).one().quantidade


async def resumo(cliente, cabecalho, id_carteira):
    return (await cliente.get(f"/portfolios/{id_carteira}/summary", headers=cabecalho)).json()


def posicao(dados, ticker):
    return next(a for a in dados["ativos"] if a["ticker"] == ticker)


async def test_cenario1_compra_bem_sucedida(cliente, banco, investidor_logado, aposentadoria, transacao):
    id_carteira = aposentadoria.id_carteira
    assert Decimal((await resumo(cliente, investidor_logado, id_carteira))["patrimonio_total"]) == Decimal("9706.00")

    resposta = await transacao(investidor_logado, id_carteira, "ITUB4", "compra", 200, data_transacao=DATA_17_11)
    assert resposta.status_code == 201
    dados = resposta.json()
    assert Decimal(dados["valor_total"]) == Decimal("8178.00")  # 200 x R$ 40,89
    assert dados["data_transacao"].startswith("2026-11-17")
    assert dados["tipo"] == "compra"
    assert dados["ticker"] == "ITUB4"
    assert dados["quantidade"] == 200
    assert dados["nome_carteira"] == "Aposentadoria"
    setor = (await cliente.get("/assets/ITUB4", headers=investidor_logado)).json()["setor"]
    assert setor == banco.get(Ativo, "ITUB4").setor  # setor vem da classificacao do papel

    assert quantidade(banco, id_carteira, "ITUB4") == 300
    depois = await resumo(cliente, investidor_logado, id_carteira)
    itub4 = posicao(depois, "ITUB4")
    assert Decimal(itub4["valor_atual"]) == Decimal("12267.00")
    assert Decimal(depois["patrimonio_total"]) == Decimal("17884.00")
    assert Decimal(itub4["participacao_percentual"]) == Decimal("68.59")
    # Distancia = participacao atual - objetivo (10%).
    assert Decimal(itub4["participacao_percentual"]) - 10 == Decimal("58.59")


async def test_cenario2_valor_total_exibido_antes_de_registrar(cliente, banco, investidor_logado, aposentadoria):
    cotacao = (await cliente.get("/quotes/ITUB4", headers=investidor_logado)).json()
    assert Decimal(cotacao["preco"]) * 200 == Decimal("8178.00")
    # Consultar a cotacao nao grava nada.
    assert banco.query(Transacao).count() == 0
    assert quantidade(banco, aposentadoria.id_carteira, "ITUB4") == 100


async def test_cenario3_compra_de_lote_maior(banco, investidor_logado, aposentadoria, transacao):
    resposta = await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)
    assert resposta.status_code == 201
    assert Decimal(resposta.json()["valor_total"]) == Decimal("8178.00")
    assert quantidade(banco, aposentadoria.id_carteira, "ITUB4") == 300


# ---------- regras extras ----------

async def test_preco_informado_e_o_que_fica_salvo(investidor_logado, aposentadoria, transacao, yahoo):
    yahoo.consultas.clear()
    resposta = await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 100, preco="40.50")
    assert Decimal(resposta.json()["preco_unitario"]) == Decimal("40.50")
    assert yahoo.consultas == []  # a cotacao atual nao substitui o preco pago


async def test_ticker_em_minusculas_e_aceito(investidor_logado, aposentadoria, transacao):
    resposta = await transacao(investidor_logado, aposentadoria.id_carteira, "itub4", "compra", 100)
    assert resposta.status_code == 201
    assert resposta.json()["ticker"] == "ITUB4"


async def test_ativo_desativado_nao_pode_ser_comprado(banco, investidor_logado, aposentadoria, transacao):
    banco.get(Ativo, "ITUB4").ativo = False
    banco.commit()
    resposta = await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 100)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O ativo está desativado."
    assert quantidade(banco, aposentadoria.id_carteira, "ITUB4") == 100


async def test_carteira_desativada(cliente, investidor_logado, aposentadoria, transacao):
    await cliente.patch(f"/portfolios/{aposentadoria.id_carteira}", json={"ativa": False}, headers=investidor_logado)
    resposta = await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 100)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A carteira está desativada."
