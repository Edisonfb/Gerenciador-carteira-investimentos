"""US 11.2 - Registro de venda (SCRUM-64 e SCRUM-32)."""

from decimal import Decimal

import pytest

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.transactions.models import Transacao


@pytest.fixture
def montar_aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    """Carteira das historias, com a quantidade de ITUB4 escolhida no teste."""
    def _montar(quantidade_itub4):
        investidor = banco.query(Investidor).first()
        return criar_carteira(investidor.id_investidor, "Aposentadoria", [
            ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, quantidade_itub4),
        ])

    return _montar


def quantidade(banco, id_carteira, ticker):
    banco.expire_all()
    return banco.query(AtivoCarteira).filter_by(id_carteira=id_carteira, ticker=ticker).one().quantidade


async def resumo(cliente, cabecalho, id_carteira):
    return (await cliente.get(f"/portfolios/{id_carteira}/summary", headers=cabecalho)).json()


def participacao(dados, ticker):
    return Decimal(next(a for a in dados["ativos"] if a["ticker"] == ticker)["participacao_percentual"])


async def test_cenario1_venda_bem_sucedida(cliente, banco, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(200)
    antes = await resumo(cliente, investidor_logado, carteira.id_carteira)
    assert Decimal(antes["patrimonio_total"]) == Decimal("13795.00")
    assert participacao(antes, "ITUB4") - 10 == Decimal("49.28")

    resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "venda", 100,
                               data_transacao="2026-11-17T21:09:00-03:00")
    assert resposta.status_code == 201
    dados = resposta.json()
    assert Decimal(dados["valor_total"]) == Decimal("4089.00")  # 100 x R$ 40,89
    assert dados["tipo"] == "venda"
    assert dados["quantidade"] == 100
    assert dados["nome_carteira"] == "Aposentadoria"
    assert dados["data_transacao"].startswith("2026-11-18T00:09")  # 17/11 21:09 em Brasilia, guardado em UTC

    assert quantidade(banco, carteira.id_carteira, "ITUB4") == 100
    depois = await resumo(cliente, investidor_logado, carteira.id_carteira)
    assert Decimal(depois["patrimonio_total"]) == Decimal("9706.00")
    assert participacao(depois, "ITUB4") == Decimal("42.13")
    assert participacao(depois, "ITUB4") - 10 == Decimal("32.13")


async def test_cenario2_venda_de_toda_a_quantidade(cliente, banco, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(100)
    resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "venda", 100)
    assert resposta.status_code == 201
    assert Decimal(resposta.json()["valor_total"]) == Decimal("4089.00")
    assert quantidade(banco, carteira.id_carteira, "ITUB4") == 0

    # O ITUB4 continua na carteira, com quantidade zero.
    ativos = (await cliente.get(f"/assets/carteira/{carteira.id_carteira}", headers=investidor_logado)).json()
    assert {"ticker": "ITUB4", "quantidade": 0}.items() <= next(a for a in ativos if a["ticker"] == "ITUB4").items()


async def test_cenario3_venda_maior_que_a_quantidade(banco, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(100)
    resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "venda", 200)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Quantidade insuficiente para venda. Você possui 100 ações deste ativo."
    assert banco.query(Transacao).count() == 0
    assert quantidade(banco, carteira.id_carteira, "ITUB4") == 100


async def test_cenario4_venda_de_ativo_sem_quantidade(banco, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(0)
    resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "venda", 100)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Quantidade insuficiente para venda. Você possui 0 ações deste ativo."
    assert banco.query(Transacao).count() == 0


async def test_cenario5_venda_fora_do_lote_de_100(banco, investidor_logado, criar_carteira, transacao):
    carteira = criar_carteira(banco.query(Investidor).first().id_investidor, "Aposentadoria", [("CRFB3", 100, 200)])
    resposta = await transacao(investidor_logado, carteira.id_carteira, "CRFB3", "venda", 150)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A quantidade deve ser em lotes de 100 ações."
    assert banco.query(Transacao).count() == 0
    assert quantidade(banco, carteira.id_carteira, "CRFB3") == 200


# ---------- regras extras ----------

async def test_ativo_desativado_ainda_pode_ser_vendido(banco, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(200)
    banco.get(Ativo, "ITUB4").ativo = False
    banco.commit()
    resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "venda", 100)
    assert resposta.status_code == 201
    assert quantidade(banco, carteira.id_carteira, "ITUB4") == 100
