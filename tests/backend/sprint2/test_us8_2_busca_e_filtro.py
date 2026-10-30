"""US 8.2 - Busca e filtro de ativos por setor."""

from app.modules.assets.repository import AtivoRepository
from app.modules.assets.service import AtivoService


def test_service_busca_codigo_ignora_maiusculas_e_espacos(banco):
    encontrados = AtivoService(AtivoRepository(banco)).listar_ativos(codigo=" itub4 ")
    assert [a.ticker for a in encontrados] == ["ITUB4"]


async def test_catalogo_lista_os_ativos(cliente, investidor_logado):
    resposta = await cliente.get("/assets", headers=investidor_logado)
    assert resposta.status_code == 200
    tickers = [a["ticker"] for a in resposta.json()]
    assert "ITUB3" in tickers and "ITUB4" in tickers  # ativos distintos


async def test_cenario1_busca_por_codigo(cliente, investidor_logado):
    resposta = await cliente.get("/assets", params={"codigo": "ITUB4"}, headers=investidor_logado)
    assert [a["ticker"] for a in resposta.json()] == ["ITUB4"]


async def test_cenario2_filtro_por_setor(cliente, investidor_logado):
    resposta = await cliente.get("/assets/setor/Financeiro", headers=investidor_logado)
    assert resposta.status_code == 200
    assert resposta.json()
    assert all(a["setor"] == "Financeiro" for a in resposta.json())
    assert [a["ticker"] for a in resposta.json()] == ["BBDC3", "BBDC4", "ITUB3", "ITUB4"]


async def test_cenario3_busca_sem_resultados(cliente, investidor_logado):
    resposta = await cliente.get("/assets", params={"codigo": "QQQQ9"}, headers=investidor_logado)
    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_catalogo_exige_login(cliente):
    resposta = await cliente.get("/assets")
    assert resposta.status_code == 401
