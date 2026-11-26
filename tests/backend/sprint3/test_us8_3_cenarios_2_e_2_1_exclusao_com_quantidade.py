"""US 8.3 - Cenarios 2 e 2.1 (testados na Sprint 3).

Ativo com quantidade nao sai da carteira e carteira com ativo(s) com quantidade
nao e excluida: a pessoa precisa registrar a venda antes.
Carteira "Aposentadoria" com patrimonio de R$ 10.000,00 e CRFB3 com 200 acoes (R$ 3.000,00).
"""

import pytest

from app.modules.assets.models import AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.service import CarteiraService, ErroExclusaoCarteira


MENSAGEM_ATIVO = "Você possui quantidade desse ativo, faça um registro de venda para removê-lo da carteira."
MENSAGEM_CARTEIRA = (
    "Você possui ativo(s) nessa carteira que possuem quantidade, faça registro de venda do(s) ativo(s)."
)


@pytest.fixture
def aposentadoria(banco, investidor_logado, criar_carteira):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 10, 0), ("BBDC4", 10, 0), ("CRFB3", 40, 200), ("EGIE3", 20, 0), ("ITUB4", 20, 100),
    ])


async def vender(cliente, cabecalho, id_carteira, ticker, quantidade):
    resposta = await cliente.post("/transactions", headers=cabecalho, json={
        "id_carteira": id_carteira, "ticker": ticker, "tipo": "venda",
        "quantidade": quantidade, "preco_unitario": "15.00",
    })
    assert resposta.status_code == 201, resposta.text


async def ativos_da_carteira(cliente, cabecalho, id_carteira):
    resposta = await cliente.get(f"/assets/carteira/{id_carteira}", headers=cabecalho)
    return {a["ticker"]: a["quantidade"] for a in resposta.json()}


# ---------- Cenario 2: remocao de ativo que ja possui quantidade ----------

async def test_cenario2_ativo_com_quantidade_nao_e_removido(cliente, investidor_logado, aposentadoria):
    resposta = await cliente.delete(f"/assets/carteira/{aposentadoria.id_carteira}/CRFB3", headers=investidor_logado)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == MENSAGEM_ATIVO
    # Depois de confirmar o aviso, o ativo continua na carteira com a mesma quantidade.
    assert (await ativos_da_carteira(cliente, investidor_logado, aposentadoria.id_carteira))["CRFB3"] == 200


async def test_cenario2_venda_parcial_ainda_bloqueia(cliente, investidor_logado, aposentadoria):
    await vender(cliente, investidor_logado, aposentadoria.id_carteira, "CRFB3", 100)
    resposta = await cliente.delete(f"/assets/carteira/{aposentadoria.id_carteira}/CRFB3", headers=investidor_logado)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == MENSAGEM_ATIVO


async def test_cenario2_depois_de_vender_tudo_o_ativo_e_removido(cliente, investidor_logado, aposentadoria):
    await vender(cliente, investidor_logado, aposentadoria.id_carteira, "CRFB3", 200)
    resposta = await cliente.delete(f"/assets/carteira/{aposentadoria.id_carteira}/CRFB3", headers=investidor_logado)
    assert resposta.status_code == 204
    assert "CRFB3" not in await ativos_da_carteira(cliente, investidor_logado, aposentadoria.id_carteira)


async def test_cenario2_ativo_sem_quantidade_sai_normalmente(cliente, investidor_logado, aposentadoria):
    resposta = await cliente.delete(f"/assets/carteira/{aposentadoria.id_carteira}/ABEV3", headers=investidor_logado)
    assert resposta.status_code == 204


# ---------- Cenario 2.1: exclusao da carteira com ativos que tem quantidade ----------

async def test_cenario2_1_carteira_com_quantidade_nao_e_excluida(cliente, banco, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    resposta = await cliente.delete(f"/portfolios/{id_carteira}", headers=investidor_logado)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == MENSAGEM_CARTEIRA

    # A carteira volta a aparecer na listagem, com todos os ativos.
    nomes = [c["nome"] for c in (await cliente.get("/portfolios", headers=investidor_logado)).json()]
    assert nomes == ["Aposentadoria"]
    assert banco.query(AtivoCarteira).filter_by(id_carteira=id_carteira).count() == 5


async def test_cenario2_1_basta_um_ativo_com_quantidade(cliente, investidor_logado, aposentadoria):
    await vender(cliente, investidor_logado, aposentadoria.id_carteira, "CRFB3", 200)
    resposta = await cliente.delete(f"/portfolios/{aposentadoria.id_carteira}", headers=investidor_logado)
    assert resposta.status_code == 400  # ITUB4 ainda tem 100 acoes
    assert resposta.json()["detail"] == MENSAGEM_CARTEIRA


async def test_cenario2_1_depois_de_vender_tudo_a_carteira_e_excluida(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    await vender(cliente, investidor_logado, id_carteira, "CRFB3", 200)
    await vender(cliente, investidor_logado, id_carteira, "ITUB4", 100)
    resposta = await cliente.delete(f"/portfolios/{id_carteira}", headers=investidor_logado)
    assert resposta.status_code == 204
    assert (await cliente.get("/portfolios", headers=investidor_logado)).json() == []


async def test_cenario2_1_carteira_sem_quantidade_e_excluida(cliente, banco, investidor_logado, criar_carteira):
    investidor = banco.query(Investidor).first()
    carro = criar_carteira(investidor.id_investidor, "Carro", [("AALR3", 100, 0)])
    resposta = await cliente.delete(f"/portfolios/{carro.id_carteira}", headers=investidor_logado)
    assert resposta.status_code == 204


def test_cenario2_1_service_bloqueia_a_exclusao(banco, criar_investidor, criar_carteira):
    dono = criar_investidor()
    carteira = criar_carteira(dono.id_investidor, "Aposentadoria", [("CRFB3", 100, 200)])
    with pytest.raises(ErroExclusaoCarteira) as erro:
        CarteiraService(CarteiraRepository(banco)).excluir_carteira(carteira.id_carteira, dono.id_investidor)
    assert str(erro.value) == MENSAGEM_CARTEIRA
    assert erro.value.status_code == 400


def test_cenario2_1_repository_confere_quantidade(banco, criar_investidor, criar_carteira):
    dono = criar_investidor()
    com = criar_carteira(dono.id_investidor, "Com", [("CRFB3", 50, 200), ("ABEV3", 50, 0)])
    sem = criar_carteira(dono.id_investidor, "Sem", [("CRFB3", 50, 0), ("ABEV3", 50, 0)])
    vazia = criar_carteira(dono.id_investidor, "Vazia")
    repositorio = CarteiraRepository(banco)
    assert repositorio.possui_ativo_com_quantidade(com.id_carteira) is True
    assert repositorio.possui_ativo_com_quantidade(sem.id_carteira) is False
    assert repositorio.possui_ativo_com_quantidade(vazia.id_carteira) is False
