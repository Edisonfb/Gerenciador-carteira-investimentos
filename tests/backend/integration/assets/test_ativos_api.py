"""Verifica o router de ativos com autenticação real e banco em memória."""

import pytest

from app.core.security import criar_token_acesso
from app.modules.assets.models import Ativo


@pytest.fixture
def catalogo(sessao_banco):
    """Prepara ativos compartilhados, independentemente de carteiras."""
    ativos = [
        Ativo(codigo="VALE3", setor="Mineração"),
        Ativo(codigo="PETR4", setor="Petróleo"),
    ]
    sessao_banco.add_all(ativos)
    sessao_banco.commit()
    return ativos


@pytest.fixture
def autorizacao(criar_investidor):
    """Emite um token real de um investidor cadastrado no banco de teste."""
    investidor = criar_investidor()
    return {"Authorization": f"Bearer {criar_token_acesso(investidor.id_usuario)}"}


async def test_listagem_retorna_catalogo_ordenado(cliente, catalogo, autorizacao):
    """Retorna os ativos em ordem de código e serializa os modelos do banco."""
    resposta = await cliente.get("/assets", headers=autorizacao)

    assert resposta.status_code == 200
    dados = resposta.json()
    assert [ativo["codigo"] for ativo in dados] == ["PETR4", "VALE3"]
    assert set(dados[0]) == {"id_ativo", "codigo", "setor", "ativo", "data_criacao"}
    assert dados[0]["ativo"] is True
    assert dados[0]["data_criacao"]


async def test_listagem_sem_registros(cliente, autorizacao):
    """Uma consulta válida ao catálogo vazio retorna uma lista vazia."""
    resposta = await cliente.get("/assets", headers=autorizacao)

    assert resposta.status_code == 200
    assert resposta.json() == []


@pytest.mark.parametrize("codigo,esperados", [(" petr4 ", ["PETR4"]), ("PETR", [])])
async def test_filtro_por_codigo_exato(cliente, catalogo, autorizacao, codigo, esperados):
    """Normaliza espaços e caixa, mantendo a pesquisa por igualdade de código."""
    resposta = await cliente.get(
        "/assets", params={"codigo": codigo}, headers=autorizacao
    )

    assert resposta.status_code == 200
    assert [ativo["codigo"] for ativo in resposta.json()] == esperados


async def test_consulta_por_id(cliente, catalogo, autorizacao):
    """Consulta o registro identificado pelo ID fornecido na URL."""
    resposta = await cliente.get(f"/assets/{catalogo[0].id_ativo}", headers=autorizacao)

    assert resposta.status_code == 200
    assert resposta.json()["codigo"] == "VALE3"


async def test_id_inexistente_retorna_404(cliente, autorizacao):
    """Distingue um recurso inexistente de uma lista vazia."""
    resposta = await cliente.get("/assets/999", headers=autorizacao)

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Ativo não encontrado."}


@pytest.mark.parametrize("caminho", ["/assets", "/assets/1"])
async def test_consulta_exige_login(cliente, caminho):
    """Impede consultar o catálogo sem autenticação."""
    resposta = await cliente.get(caminho)

    assert resposta.status_code == 401


@pytest.mark.parametrize("caminho", ["/assets", "/assets/1"])
async def test_consulta_restrita_a_investidor(cliente, criar_analista, caminho):
    """Aplica a restrição de perfil definida para estas rotas."""
    analista = criar_analista()
    cabecalho = {"Authorization": f"Bearer {criar_token_acesso(analista.id_usuario)}"}
    resposta = await cliente.get(caminho, headers=cabecalho)

    assert resposta.status_code == 403


@pytest.mark.parametrize(
    "metodo,caminho", [("POST", "/assets"), ("PUT", "/assets/1"), ("DELETE", "/assets/1")]
)
async def test_catalogo_nao_expoe_escrita(cliente, autorizacao, metodo, caminho):
    """Garante que a API de ativos oferece somente consultas ao investidor."""
    resposta = await cliente.request(metodo, caminho, headers=autorizacao)

    assert resposta.status_code == 405
