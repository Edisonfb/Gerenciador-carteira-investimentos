"""US 19.3 - Conferencia da quantidade e historico somente leitura (SCRUM-63 e SCRUM-32)."""

from decimal import Decimal

import pytest

from app.modules.assets.models import AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.transactions.models import Transacao


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, 0),
    ])


async def historico(cliente, cabecalho, id_carteira):
    return (await cliente.get("/transactions", headers=cabecalho, params={"id_carteira": id_carteira})).json()


async def test_cenario1_quantidade_confere_com_compras_e_vendas(cliente, banco, investidor_logado, aposentadoria, transacao):
    id_carteira = aposentadoria.id_carteira
    await transacao(investidor_logado, id_carteira, "ITUB4", "compra", 200)
    await transacao(investidor_logado, id_carteira, "ITUB4", "venda", 100)

    lista = await historico(cliente, investidor_logado, id_carteira)
    saldo = sum(t["quantidade"] if t["tipo"] == "compra" else -t["quantidade"] for t in lista if t["ticker"] == "ITUB4")
    ativos = (await cliente.get(f"/assets/carteira/{id_carteira}", headers=investidor_logado)).json()
    quantidade_itub4 = next(a["quantidade"] for a in ativos if a["ticker"] == "ITUB4")
    assert saldo == quantidade_itub4 == 100


async def test_cenario2_consulta_nao_altera_a_carteira(cliente, banco, investidor_logado, aposentadoria, transacao):
    id_carteira = aposentadoria.id_carteira
    await transacao(investidor_logado, id_carteira, "ITUB4", "compra", 300)
    antes = (await cliente.get(f"/portfolios/{id_carteira}/summary", headers=investidor_logado)).json()
    assert Decimal(antes["patrimonio_total"]) == Decimal("17884.00")

    for _ in range(3):
        await historico(cliente, investidor_logado, id_carteira)

    depois = (await cliente.get(f"/portfolios/{id_carteira}/summary", headers=investidor_logado)).json()
    assert depois == antes
    assert banco.query(Transacao).count() == 1


async def test_cenario3_transacoes_nao_podem_ser_editadas_nem_excluidas(cliente, banco, investidor_logado, aposentadoria, transacao):
    criada = (await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)).json()
    caminho = f"/transactions/{criada['id_transacao']}"
    tentativas = [
        await cliente.put(caminho, json={"quantidade": 100}, headers=investidor_logado),
        await cliente.patch(caminho, json={"quantidade": 100}, headers=investidor_logado),
        await cliente.delete(caminho, headers=investidor_logado),
        await cliente.delete("/transactions", headers=investidor_logado),
    ]
    # Nao existe rota para editar ou excluir transacoes.
    assert all(r.status_code in (404, 405) for r in tentativas)

    banco.expire_all()
    assert banco.query(Transacao).one().quantidade == 200
    assert banco.query(AtivoCarteira).filter_by(id_carteira=aposentadoria.id_carteira, ticker="ITUB4").one().quantidade == 200
