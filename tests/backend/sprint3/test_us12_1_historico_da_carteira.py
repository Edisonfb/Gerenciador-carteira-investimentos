"""US 12.1 - Consulta do historico de transacoes da carteira (SCRUM-63)."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.modules.investors.models import Investidor


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [("EGIE3", 50, 0), ("ITUB4", 50, 0)])


@pytest.fixture
async def quatro_transacoes(investidor_logado, aposentadoria, transacao):
    """As quatro transacoes de 17/11/2026 da historia, na ordem em que foram feitas."""
    for ticker, tipo, qtd, hora in [("ITUB4", "compra", 200, "10:00"), ("EGIE3", "compra", 100, "11:00"),
                                    ("ITUB4", "venda", 100, "12:00"), ("ITUB4", "compra", 100, "13:00")]:
        resposta = await transacao(investidor_logado, aposentadoria.id_carteira, ticker, tipo, qtd,
                                   data_transacao=f"2026-11-17T{hora}:00-03:00")
        assert resposta.status_code == 201, resposta.text


async def historico(cliente, cabecalho, id_carteira, **filtros):
    resposta = await cliente.get("/transactions", headers=cabecalho, params={"id_carteira": id_carteira, **filtros})
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


def linhas(lista):
    return [(t["tipo"], t["ticker"], t["quantidade"], Decimal(t["valor_total"])) for t in lista]


async def test_cenario1_historico_completo_da_carteira(cliente, investidor_logado, aposentadoria, quatro_transacoes):
    lista = await historico(cliente, investidor_logado, aposentadoria.id_carteira)
    assert linhas(lista) == [
        ("compra", "ITUB4", 100, Decimal("4089.00")),
        ("venda", "ITUB4", 100, Decimal("4089.00")),
        ("compra", "EGIE3", 100, Decimal("2583.00")),
        ("compra", "ITUB4", 200, Decimal("8178.00")),
    ]
    assert all(t["data_transacao"].startswith("2026-11-17") for t in lista)
    # O setor de cada linha vem da classificacao do papel no catalogo de ativos.
    for ticker, setor in [("ITUB4", "Financeiro"), ("EGIE3", "Utilidade Pública")]:
        assert (await cliente.get(f"/assets/{ticker}", headers=investidor_logado)).json()["setor"] == setor


async def test_cenario2_compra_e_venda_aparecem_como_tipos_distintos(cliente, investidor_logado, aposentadoria, quatro_transacoes):
    lista = await historico(cliente, investidor_logado, aposentadoria.id_carteira, ticker="ITUB4")
    assert {t["tipo"] for t in lista} == {"compra", "venda"}
    assert [t["tipo"] for t in await historico(cliente, investidor_logado, aposentadoria.id_carteira, tipo="venda")] == ["venda"]


async def test_cenario3_ordem_da_mais_recente_para_a_mais_antiga(cliente, investidor_logado, aposentadoria, transacao):
    # Lancadas fora de ordem de proposito.
    for dia in ["12", "26", "05", "19"]:
        await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 100,
                        data_transacao=f"2026-10-{dia}T12:00:00-03:00")
    datas = [t["data_transacao"][:10] for t in await historico(cliente, investidor_logado, aposentadoria.id_carteira)]
    assert datas == ["2026-10-26", "2026-10-19", "2026-10-12", "2026-10-05"]


async def test_cenario4_carteira_sem_transacoes(cliente, investidor_logado, aposentadoria):
    assert await historico(cliente, investidor_logado, aposentadoria.id_carteira) == []


async def test_cenario5_nova_transacao_passa_a_aparecer(cliente, investidor_logado, aposentadoria, quatro_transacoes, transacao):
    assert len(await historico(cliente, investidor_logado, aposentadoria.id_carteira)) == 4
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 100)

    lista = await historico(cliente, investidor_logado, aposentadoria.id_carteira)
    assert len(lista) == 5
    nova = lista[0]
    assert (nova["tipo"], nova["ticker"], nova["quantidade"], Decimal(nova["valor_total"])) == ("compra", "ITUB4", 100, Decimal("4089.00"))
    assert nova["data_transacao"][:10] == datetime.now(timezone.utc).strftime("%Y-%m-%d")  # data do registro


# ---------- regras extras ----------

async def test_tipo_invalido_no_filtro(cliente, investidor_logado, aposentadoria):
    resposta = await cliente.get("/transactions", headers=investidor_logado, params={"tipo": "deposito"})
    assert resposta.status_code == 422


async def test_sem_login(cliente):
    assert (await cliente.get("/transactions")).status_code == 401
