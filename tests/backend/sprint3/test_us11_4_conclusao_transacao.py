"""US 11.4 - Distincao entre compra e venda e conclusao da transacao (SCRUM-64 e SCRUM-32).

O cenario 1 (destaque do tipo na tela) e so do frontend. O cenario 3 e opcional
e fica em test_opcionais_us11_4.py.
"""

import pytest

from app.modules.assets.models import AtivoCarteira
from app.modules.investors.models import Investidor


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, 100),
    ])


def quantidade(banco, id_carteira, ticker):
    banco.expire_all()
    return banco.query(AtivoCarteira).filter_by(id_carteira=id_carteira, ticker=ticker).one().quantidade


async def test_cenario2_transacao_concluida_com_a_carteira_atualizada(cliente, banco, investidor_logado, aposentadoria, transacao):
    id_carteira = aposentadoria.id_carteira
    resposta = await transacao(investidor_logado, id_carteira, "ITUB4", "compra", 200)
    assert resposta.status_code == 201
    assert quantidade(banco, id_carteira, "ITUB4") == 300

    historico = (await cliente.get("/transactions", headers=investidor_logado, params={"id_carteira": id_carteira})).json()
    assert [t["id_transacao"] for t in historico] == [resposta.json()["id_transacao"]]


async def test_compra_e_venda_tem_efeitos_opostos(banco, investidor_logado, aposentadoria, transacao):
    # Compra soma e venda subtrai: o tipo escolhido define o que acontece com a carteira.
    id_carteira = aposentadoria.id_carteira
    await transacao(investidor_logado, id_carteira, "ITUB4", "compra", 100)
    assert quantidade(banco, id_carteira, "ITUB4") == 200
    await transacao(investidor_logado, id_carteira, "ITUB4", "venda", 100)
    assert quantidade(banco, id_carteira, "ITUB4") == 100


async def test_transacao_nao_altera_outra_carteira(banco, investidor_logado, aposentadoria, criar_carteira, transacao):
    casa = criar_carteira(aposentadoria.id_investidor, "Casa", [("ITUB4", 100, 0)])
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)
    assert quantidade(banco, casa.id_carteira, "ITUB4") == 0
