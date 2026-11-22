"""SCRUM-28 - Calcular patrimonio total da carteira (soma do patrimonio dos ativos).

Valores da carteira "Aposentadoria" das US 11.1 e 11.2 (cotacoes de 17/11/2026).
"""

from decimal import Decimal

import pytest

from app.modules.investors.models import Investidor
from app.modules.portfolios.calculos import CalculosCarteira


@pytest.fixture
def montar_aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    def _montar(quantidade_itub4):
        investidor = banco.query(Investidor).first()
        return criar_carteira(investidor.id_investidor, "Aposentadoria", [
            ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, quantidade_itub4),
        ])

    return _montar


async def resumo(cliente, cabecalho, id_carteira):
    return await cliente.get(f"/portfolios/{id_carteira}/summary", headers=cabecalho)


# ---------- unitarios ----------

def test_patrimonio_total_soma_as_posicoes():
    valores = [Decimal("1593.00"), Decimal("1441.00"), Decimal("2583.00"), Decimal("4089.00")]
    assert CalculosCarteira.patrimonio_total(valores) == Decimal("9706.00")


def test_patrimonio_total_sem_posicoes_e_zero():
    assert CalculosCarteira.patrimonio_total([]) == Decimal("0.00")


# ---------- API ----------

@pytest.mark.parametrize("quantidade_itub4, total", [(100, "9706.00"), (200, "13795.00"), (300, "17884.00")])
async def test_patrimonio_total_da_carteira(cliente, investidor_logado, montar_aposentadoria, quantidade_itub4, total):
    carteira = montar_aposentadoria(quantidade_itub4)
    resposta = await resumo(cliente, investidor_logado, carteira.id_carteira)
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["id_carteira"] == carteira.id_carteira
    assert Decimal(dados["patrimonio_total"]) == Decimal(total)
    assert sum(Decimal(a["valor_atual"]) for a in dados["ativos"]) == Decimal(total)


async def test_carteira_sem_ativos_tem_patrimonio_zero(cliente, banco, investidor_logado, criar_carteira, yahoo):
    carteira = criar_carteira(banco.query(Investidor).first().id_investidor, "Casa")
    resposta = await resumo(cliente, investidor_logado, carteira.id_carteira)
    assert resposta.status_code == 200
    assert Decimal(resposta.json()["patrimonio_total"]) == 0
    assert resposta.json()["ativos"] == []


async def test_carteira_so_com_quantidade_zero_tem_patrimonio_zero(cliente, banco, investidor_logado, criar_carteira, yahoo):
    # Carteira "Casa" da US 12.2: quatro ativos, todos com quantidade 0.
    carteira = criar_carteira(banco.query(Investidor).first().id_investidor, "Casa",
                              [("AALR3", 25, 0), ("ABEV3", 25, 0), ("EGIE3", 25, 0), ("ITUB4", 25, 0)])
    dados = (await resumo(cliente, investidor_logado, carteira.id_carteira)).json()
    assert Decimal(dados["patrimonio_total"]) == 0
    assert all(Decimal(a["participacao_percentual"]) == 0 for a in dados["ativos"])


async def test_patrimonio_muda_depois_de_compra_e_venda(cliente, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(100)
    await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "compra", 200)
    assert Decimal((await resumo(cliente, investidor_logado, carteira.id_carteira)).json()["patrimonio_total"]) == Decimal("17884.00")
    await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "venda", 200)
    assert Decimal((await resumo(cliente, investidor_logado, carteira.id_carteira)).json()["patrimonio_total"]) == Decimal("9706.00")


async def test_patrimonio_usa_a_cotacao_atual_e_nao_o_preco_pago(cliente, investidor_logado, montar_aposentadoria, transacao):
    carteira = montar_aposentadoria(100)
    await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "compra", 200, preco="38.00")
    assert Decimal((await resumo(cliente, investidor_logado, carteira.id_carteira)).json()["patrimonio_total"]) == Decimal("17884.00")


async def test_carteira_de_outro_investidor(cliente, montar_aposentadoria, criar_investidor, login):
    carteira = montar_aposentadoria(100)
    criar_investidor(nome_usuario="carlos.lima", senha="Carlos@2025", email="carlos.lima@example.test",
                     email_recuperacao="carlos.lima2@example.test")
    resposta = await resumo(cliente, await login("carlos.lima", "Carlos@2025"), carteira.id_carteira)
    assert resposta.status_code == 404


async def test_carteira_inexistente(cliente, investidor_logado, yahoo):
    resposta = await resumo(cliente, investidor_logado, 999)
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Carteira não encontrada."


async def test_cotacao_indisponivel_sem_cotacao_salva(cliente, investidor_logado, montar_aposentadoria, yahoo):
    carteira = montar_aposentadoria(100)
    del yahoo.precos["ABEV3"]
    resposta = await resumo(cliente, investidor_logado, carteira.id_carteira)
    assert resposta.status_code == 503
    assert "ABEV3" in resposta.json()["detail"]


async def test_sem_login(cliente, montar_aposentadoria):
    carteira = montar_aposentadoria(100)
    resposta = await cliente.get(f"/portfolios/{carteira.id_carteira}/summary")
    assert resposta.status_code == 401
