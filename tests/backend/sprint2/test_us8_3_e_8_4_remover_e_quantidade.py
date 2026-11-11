"""US 8.3 - Remocao de ativo da carteira / US 8.4 - Quantidade protegida."""

import pytest

from app.modules.investors.models import Investidor


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 10, 0), ("BBDC3", 10, 0), ("CRFB3", 40, 0), ("EGIE3", 20, 0), ("ITUB4", 20, 25),
    ])


async def test_us8_3_cenario1_remocao_bem_sucedida(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    resposta = await cliente.delete(f"/assets/carteira/{id_carteira}/ITUB4", headers=investidor_logado)
    assert resposta.status_code == 204

    ativos = (await cliente.get(f"/assets/carteira/{id_carteira}", headers=investidor_logado)).json()
    assert [a["ticker"] for a in ativos] == ["ABEV3", "BBDC3", "CRFB3", "EGIE3"]
    # Sem o ITUB4 os objetivos restantes somam 80% e precisam ser redistribuidos.
    assert sum(float(a["objetivo_percentual"]) for a in ativos) == 80


async def test_us8_3_remover_ativo_que_nao_esta_na_carteira(cliente, investidor_logado, aposentadoria):
    resposta = await cliente.delete(f"/assets/carteira/{aposentadoria.id_carteira}/AALR3", headers=investidor_logado)
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Ativo não encontrado nesta carteira."


async def test_us8_3_redistribuir_objetivo_depois_da_remocao(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    await cliente.delete(f"/assets/carteira/{id_carteira}/ITUB4", headers=investidor_logado)
    resposta = await cliente.patch(f"/assets/carteira/{id_carteira}/ABEV3", json={"objetivo_percentual": "30"}, headers=investidor_logado)
    assert resposta.status_code == 200

    ativos = (await cliente.get(f"/assets/carteira/{id_carteira}", headers=investidor_logado)).json()
    assert sum(float(a["objetivo_percentual"]) for a in ativos) == 100


async def test_us8_4_cenario2_editar_objetivo_preserva_a_quantidade(cliente, investidor_logado, aposentadoria):
    id_carteira = aposentadoria.id_carteira
    resposta = await cliente.patch(f"/assets/carteira/{id_carteira}/ITUB4", json={"objetivo_percentual": "25"}, headers=investidor_logado)
    assert resposta.status_code == 200
    assert resposta.json()["quantidade"] == 25


async def test_us8_4_campos_desconhecidos_sao_recusados(cliente, investidor_logado, aposentadoria):
    # Cotacao, patrimonio e participacao sao calculados pelo sistema, nao enviados.
    resposta = await cliente.patch(f"/assets/carteira/{aposentadoria.id_carteira}/ITUB4",
                                   json={"cotacao": "30.00"}, headers=investidor_logado)
    assert resposta.status_code == 422
