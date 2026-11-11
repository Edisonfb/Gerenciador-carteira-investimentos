"""US 7.1 - Criacao de carteira."""

from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.schemas import CarteiraCadastroEntrada
from app.modules.portfolios.service import CarteiraService

OBJETIVOS = {"ABEV3": "10", "BBDC3": "10", "CRFB3": "40", "EGIE3": "20", "ITUB4": "20"}


async def criar_com_ativos(cliente, cabecalho, nome, objetivos):
    """Mesmo caminho do front: cria a carteira e inclui cada ativo com quantidade zero."""
    carteira = await cliente.post("/portfolios", json={"nome": nome}, headers=cabecalho)
    assert carteira.status_code == 201, carteira.text
    id_carteira = carteira.json()["id_carteira"]
    for ticker, objetivo in objetivos.items():
        resposta = await cliente.post("/assets/carteira", headers=cabecalho, json={
            "ticker": ticker, "id_carteira": id_carteira, "quantidade": 0, "objetivo_percentual": objetivo,
        })
        assert resposta.status_code == 201, resposta.text
    return id_carteira


# ---------- unitarios (service) ----------

def test_service_cria_carteira_sem_espacos_no_nome(banco, criar_investidor):
    investidor = criar_investidor()
    carteira, erro = CarteiraService(CarteiraRepository(banco)).criar_carteira(
        CarteiraCadastroEntrada(nome="  Aposentadoria  "), investidor.id_investidor,
    )
    assert erro is None
    assert carteira.nome == "Aposentadoria"
    assert carteira.ativa is True


def test_service_nome_em_branco_nao_cria(banco, criar_investidor):
    investidor = criar_investidor()
    carteira, erro = CarteiraService(CarteiraRepository(banco)).criar_carteira(
        CarteiraCadastroEntrada(nome="   "), investidor.id_investidor,
    )
    assert carteira is None
    assert erro == "O nome da carteira é obrigatório."


# ---------- API ----------

async def test_cenario1_criacao_bem_sucedida(cliente, investidor_logado):
    id_carteira = await criar_com_ativos(cliente, investidor_logado, "Aposentadoria", OBJETIVOS)

    carteiras = await cliente.get("/portfolios", headers=investidor_logado)
    assert [c["nome"] for c in carteiras.json()] == ["Aposentadoria"]

    ativos = (await cliente.get(f"/assets/carteira/{id_carteira}", headers=investidor_logado)).json()
    assert {a["ticker"] for a in ativos} == set(OBJETIVOS)
    assert all(a["quantidade"] == 0 for a in ativos)
    assert sum(float(a["objetivo_percentual"]) for a in ativos) == 100


async def test_cenario2_nome_da_carteira_em_branco(cliente, investidor_logado):
    resposta = await cliente.post("/portfolios", json={"nome": "   "}, headers=investidor_logado)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O nome da carteira é obrigatório."

    carteiras = await cliente.get("/portfolios", headers=investidor_logado)
    assert carteiras.json() == []


async def test_cenario4_varias_carteiras_com_ativos_proprios(cliente, investidor_logado):
    id_aposentadoria = await criar_com_ativos(cliente, investidor_logado, "Aposentadoria", OBJETIVOS)
    id_carro = await criar_com_ativos(cliente, investidor_logado, "Carro", {"AALR3": "20", "ITUB3": "80"})

    nomes = [c["nome"] for c in (await cliente.get("/portfolios", headers=investidor_logado)).json()]
    assert nomes == ["Aposentadoria", "Carro"]

    ativos_carro = (await cliente.get(f"/assets/carteira/{id_carro}", headers=investidor_logado)).json()
    ativos_aposentadoria = (await cliente.get(f"/assets/carteira/{id_aposentadoria}", headers=investidor_logado)).json()
    assert [a["ticker"] for a in ativos_carro] == ["AALR3", "ITUB3"]
    assert len(ativos_aposentadoria) == 5


async def test_investidor_nao_ve_carteira_de_outro(cliente, criar_investidor, criar_carteira, login):
    outro = criar_investidor(nome_usuario="carlos.lima", email="carlos@example.test", email_recuperacao="carlos2@example.test")
    carteira_do_outro = criar_carteira(outro.id_investidor, "Carro")
    criar_investidor()
    cabecalho = await login("marina.souza", "Marina@2025")

    assert (await cliente.get("/portfolios", headers=cabecalho)).json() == []
    resposta = await cliente.get(f"/portfolios/{carteira_do_outro.id_carteira}", headers=cabecalho)
    assert resposta.status_code == 404
