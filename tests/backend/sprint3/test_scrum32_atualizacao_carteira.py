"""SCRUM-32 - Atualizacao da carteira apos transacao (quantidade do ativo na carteira)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.assets.models import AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.transactions.models import Transacao


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, 100),
    ])


def quantidade(banco, id_carteira, ticker):
    banco.expire_all()
    return banco.query(AtivoCarteira).filter_by(id_carteira=id_carteira, ticker=ticker).one().quantidade


async def test_compra_soma_a_quantidade(banco, investidor_logado, aposentadoria, transacao):
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)
    assert quantidade(banco, aposentadoria.id_carteira, "ITUB4") == 300


async def test_venda_subtrai_a_quantidade(banco, investidor_logado, aposentadoria, transacao):
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "venda", 100)
    assert quantidade(banco, aposentadoria.id_carteira, "ITUB4") == 0


async def test_sequencia_de_compras_e_vendas(banco, investidor_logado, aposentadoria, transacao):
    id_carteira = aposentadoria.id_carteira
    for tipo, qtd, esperado in [("compra", 300, 400), ("venda", 200, 200), ("compra", 100, 300), ("venda", 300, 0)]:
        assert (await transacao(investidor_logado, id_carteira, "ITUB4", tipo, qtd)).status_code == 201
        assert quantidade(banco, id_carteira, "ITUB4") == esperado
    # Com 0 acoes, uma nova venda e recusada e nada muda.
    assert (await transacao(investidor_logado, id_carteira, "ITUB4", "venda", 100)).status_code == 400
    assert quantidade(banco, id_carteira, "ITUB4") == 0
    assert banco.query(Transacao).count() == 4


async def test_so_o_ativo_negociado_muda(banco, investidor_logado, aposentadoria, transacao):
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)
    for ticker in ["ABEV3", "BBDC4", "EGIE3"]:
        assert quantidade(banco, aposentadoria.id_carteira, ticker) == 100


async def test_outra_carteira_com_o_mesmo_ativo_nao_muda(banco, investidor_logado, aposentadoria, criar_carteira, transacao):
    casa = criar_carteira(aposentadoria.id_investidor, "Casa", [("ITUB4", 100, 200)])
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)
    assert quantidade(banco, casa.id_carteira, "ITUB4") == 200


async def test_objetivo_do_ativo_nao_muda(banco, investidor_logado, aposentadoria, transacao):
    await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)
    banco.expire_all()
    ativo = banco.query(AtivoCarteira).filter_by(id_carteira=aposentadoria.id_carteira, ticker="ITUB4").one()
    assert ativo.objetivo_percentual == 10


async def test_compra_acima_do_limite_de_quantidade(banco, investidor_logado, criar_carteira, transacao):
    carteira = criar_carteira(banco.query(Investidor).first().id_investidor, "Grande", [("ITUB4", 100, 2147483600)])
    resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "compra", 100)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Quantidade acima do limite permitido."
    assert quantidade(banco, carteira.id_carteira, "ITUB4") == 2147483600
    assert banco.query(Transacao).count() == 0


async def test_falha_ao_gravar_nao_salva_transacao_nem_quantidade(banco, investidor_logado, aposentadoria, transacao, monkeypatch):
    def falha_ao_gravar(self):
        raise IntegrityError("INSERT", {}, Exception("falha simulada"))

    with monkeypatch.context() as falso:
        falso.setattr(Session, "commit", falha_ao_gravar)
        resposta = await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)

    assert resposta.status_code == 409
    banco.expire_all()
    assert banco.query(Transacao).count() == 0
    assert quantidade(banco, aposentadoria.id_carteira, "ITUB4") == 100
