"""US 8.1 - Inclusao de ativo na carteira."""

import pytest

from app.modules.investors.models import Investidor
from app.shared.validators import validar_codigo_ativo


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria",
                          [("ABEV3", 10), ("BBDC3", 10), ("CRFB3", 10), ("EGIE3", 10)])


async def incluir(cliente, cabecalho, id_carteira, ticker, objetivo="20"):
    return await cliente.post("/assets/carteira", headers=cabecalho, json={
        "ticker": ticker, "id_carteira": id_carteira, "quantidade": 0, "objetivo_percentual": objetivo,
    })


async def tickers(cliente, cabecalho, id_carteira):
    return [a["ticker"] for a in (await cliente.get(f"/assets/carteira/{id_carteira}", headers=cabecalho)).json()]


# ---------- unitarios (validador do codigo) ----------

@pytest.mark.parametrize("codigo", ["ITUB4", "itub4", "ITUB3", "ABEV3", "B3SA3"])
def test_validador_aceita_codigo_valido(codigo):
    assert validar_codigo_ativo(codigo) is True


@pytest.mark.parametrize("codigo", ["ITUB-4", "ITUB 4", "ITU4", "ITUB", "ZZZZ9", "", None])
def test_validador_recusa_codigo_invalido(codigo):
    assert validar_codigo_ativo(codigo) is False


# ---------- API ----------

async def test_cenario1_inclusao_bem_sucedida(cliente, investidor_logado, aposentadoria):
    resposta = await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ITUB4", "20")
    assert resposta.status_code == 201
    assert resposta.json()["quantidade"] == 0
    assert float(resposta.json()["objetivo_percentual"]) == 20

    setor = (await cliente.get("/assets/ITUB4", headers=investidor_logado)).json()["setor"]
    assert setor == "Financeiro"
    assert "ITUB4" in await tickers(cliente, investidor_logado, aposentadoria.id_carteira)


async def test_cenario2_codigo_com_caractere_especial(cliente, investidor_logado, aposentadoria):
    resposta = await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ITUB-4")
    assert resposta.status_code == 422
    assert await tickers(cliente, investidor_logado, aposentadoria.id_carteira) == ["ABEV3", "BBDC3", "CRFB3", "EGIE3"]


async def test_cenario3_codigo_com_tres_letras(cliente, investidor_logado, aposentadoria):
    resposta = await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ITU4")
    assert resposta.status_code == 404
    assert "ITU4" not in await tickers(cliente, investidor_logado, aposentadoria.id_carteira)


async def test_cenario4_codigo_fora_da_lista_de_ativos(cliente, investidor_logado, aposentadoria):
    resposta = await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ZZZZ9")
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Ativo não encontrado."


async def test_cenario5_ativo_ja_incluido(cliente, investidor_logado, aposentadoria):
    await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ITUB4")
    resposta = await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ITUB4")
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "O ativo já está cadastrado nesta carteira."
    assert (await tickers(cliente, investidor_logado, aposentadoria.id_carteira)).count("ITUB4") == 1


async def test_objetivo_zero_e_recusado(cliente, investidor_logado, aposentadoria):
    resposta = await incluir(cliente, investidor_logado, aposentadoria.id_carteira, "ITUB4", "0")
    assert resposta.status_code == 422


async def test_quantidade_negativa_e_recusada(cliente, investidor_logado, aposentadoria):
    resposta = await cliente.post("/assets/carteira", headers=investidor_logado, json={
        "ticker": "ITUB4", "id_carteira": aposentadoria.id_carteira, "quantidade": -1, "objetivo_percentual": "20",
    })
    assert resposta.status_code == 422
