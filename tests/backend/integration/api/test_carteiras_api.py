"""Task: Gerenciamento de carteira de investimento, pelos endpoints HTTP."""

import pytest

from app.modules.portfolios.models import Carteira


bug_descricao = pytest.mark.xfail(
    reason=(
        "Bug: o modelo Carteira nao tem a coluna 'descricao'. Criar carteira da "
        "TypeError e qualquer resposta com carteira falha na validacao de "
        "CarteiraSaida (descricao obrigatoria) -> erro 500."
    ),
    strict=True,
)


@pytest.fixture
async def investidor_logado(criar_investidor, login):
    investidor = criar_investidor()
    return investidor, await login("investidor@teste.com")


@pytest.fixture
def criar_carteira(sessao_banco):
    def _criar(investidor, nome="Aposentadoria"):
        carteira = Carteira(id_investidor=investidor.id_investidor, nome=nome)
        sessao_banco.add(carteira)
        sessao_banco.commit()
        return carteira

    return _criar


# Acesso


async def test_carteiras_exigem_token(cliente):
    resposta = await cliente.get("/portfolios")

    assert resposta.status_code == 401


async def test_analista_nao_gerencia_carteiras(cliente, criar_analista, login):
    criar_analista()
    cabecalho = await login("analista@teste.com")

    resposta = await cliente.get("/portfolios", headers=cabecalho)

    assert resposta.status_code == 403


# Criacao


@bug_descricao
async def test_cria_carteira(cliente, investidor_logado):
    investidor, cabecalho = investidor_logado

    resposta = await cliente.post(
        "/portfolios",
        json={"nome": "  Aposentadoria  ", "descricao": "Longo prazo"},
        headers=cabecalho,
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome"] == "Aposentadoria"
    assert corpo["descricao"] == "Longo prazo"
    assert corpo["id_investidor"] == investidor.id_investidor
    assert corpo["ativa"] is True


async def test_criacao_sem_nome_retorna_400(cliente, investidor_logado):
    _, cabecalho = investidor_logado

    resposta = await cliente.post("/portfolios", json={"nome": "   "}, headers=cabecalho)

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O nome da carteira é obrigatório."


async def test_criacao_com_campo_desconhecido_retorna_422(cliente, investidor_logado):
    _, cabecalho = investidor_logado

    resposta = await cliente.post(
        "/portfolios", json={"nome": "X", "saldo": 100}, headers=cabecalho
    )

    assert resposta.status_code == 422


# Consulta


async def test_lista_vazia_para_investidor_sem_carteiras(cliente, investidor_logado):
    _, cabecalho = investidor_logado

    resposta = await cliente.get("/portfolios", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.json() == []


@bug_descricao
async def test_lista_apenas_as_proprias_carteiras(
    cliente, investidor_logado, criar_investidor, criar_carteira
):
    investidor, cabecalho = investidor_logado
    outro = criar_investidor(email="outro@teste.com")
    criar_carteira(investidor, nome="Minha")
    criar_carteira(outro, nome="Dele")

    resposta = await cliente.get("/portfolios", headers=cabecalho)

    assert resposta.status_code == 200
    assert [c["nome"] for c in resposta.json()] == ["Minha"]


@bug_descricao
async def test_busca_carteira_por_id(cliente, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)

    resposta = await cliente.get(f"/portfolios/{carteira.id_carteira}", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.json()["id_carteira"] == carteira.id_carteira


async def test_carteira_de_outro_investidor_retorna_404(
    cliente, investidor_logado, criar_investidor, criar_carteira
):
    _, cabecalho = investidor_logado
    carteira_alheia = criar_carteira(criar_investidor(email="outro@teste.com"))

    resposta = await cliente.get(
        f"/portfolios/{carteira_alheia.id_carteira}", headers=cabecalho
    )

    assert resposta.status_code == 404


async def test_carteira_inexistente_retorna_404(cliente, investidor_logado):
    _, cabecalho = investidor_logado

    resposta = await cliente.get("/portfolios/999", headers=cabecalho)

    assert resposta.status_code == 404


# Atualizacao


@bug_descricao
async def test_atualiza_carteira(cliente, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor, nome="Antigo")

    resposta = await cliente.patch(
        f"/portfolios/{carteira.id_carteira}",
        json={"nome": "Novo", "ativa": False},
        headers=cabecalho,
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Novo"
    assert resposta.json()["ativa"] is False


async def test_atualizacao_com_nome_vazio_retorna_400(
    cliente, investidor_logado, criar_carteira
):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)

    resposta = await cliente.patch(
        f"/portfolios/{carteira.id_carteira}", json={"nome": "  "}, headers=cabecalho
    )

    assert resposta.status_code == 400


async def test_atualizacao_de_carteira_alheia_retorna_404(
    cliente, investidor_logado, criar_investidor, criar_carteira
):
    _, cabecalho = investidor_logado
    carteira_alheia = criar_carteira(criar_investidor(email="outro@teste.com"), nome="Dele")

    resposta = await cliente.patch(
        f"/portfolios/{carteira_alheia.id_carteira}",
        json={"nome": "Invadida"},
        headers=cabecalho,
    )

    assert resposta.status_code == 404


# Exclusao


async def test_exclui_carteira(cliente, sessao_banco, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    id_carteira = criar_carteira(investidor).id_carteira

    resposta = await cliente.delete(f"/portfolios/{id_carteira}", headers=cabecalho)

    assert resposta.status_code == 204
    sessao_banco.expire_all()
    assert sessao_banco.get(Carteira, id_carteira) is None


async def test_exclusao_de_carteira_alheia_retorna_404(
    cliente, sessao_banco, investidor_logado, criar_investidor, criar_carteira
):
    _, cabecalho = investidor_logado
    id_carteira = criar_carteira(criar_investidor(email="outro@teste.com")).id_carteira

    resposta = await cliente.delete(f"/portfolios/{id_carteira}", headers=cabecalho)

    assert resposta.status_code == 404
    sessao_banco.expire_all()
    assert sessao_banco.get(Carteira, id_carteira) is not None
