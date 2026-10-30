"""US 7.2 - Alteracao de carteira."""

import pytest

from app.modules.investors.models import Investidor


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [("AALR3", 20, 5), ("ITUB4", 80, 25)])


async def test_cenario1_alteracao_do_nome_mantem_os_ativos(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    resposta = await cliente.patch(f"/portfolios/{id_carteira}", json={"nome": "Aposentadoria 2040"}, headers=investidor_logado)
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Aposentadoria 2040"

    ativos = (await cliente.get(f"/assets/carteira/{id_carteira}", headers=investidor_logado)).json()
    assert {(a["ticker"], a["quantidade"]) for a in ativos} == {("AALR3", 5), ("ITUB4", 25)}


async def test_cenario2_nome_em_branco_nao_salva(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    resposta = await cliente.patch(f"/portfolios/{id_carteira}", json={"nome": ""}, headers=investidor_logado)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O nome da carteira é obrigatório."

    carteira = (await cliente.get(f"/portfolios/{id_carteira}", headers=investidor_logado)).json()
    assert carteira["nome"] == "Aposentadoria"


async def test_alterar_objetivo_de_um_ativo(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    resposta = await cliente.patch(f"/assets/carteira/{id_carteira}/AALR3", json={"objetivo_percentual": "30"}, headers=investidor_logado)
    assert resposta.status_code == 200
    assert float(resposta.json()["objetivo_percentual"]) == 30


async def test_alterar_carteira_inexistente(cliente, investidor_logado):
    resposta = await cliente.patch("/portfolios/999", json={"nome": "Viagem"}, headers=investidor_logado)
    assert resposta.status_code == 404
