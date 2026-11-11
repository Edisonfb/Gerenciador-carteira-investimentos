"""US 5.1 - Geracao de token de acesso para novo investidor (analista)."""

import pytest

from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import CadastroInvestidorEntrada
from app.modules.investors.service import InvestidorService


@pytest.fixture
async def analista_logado(criar_analista, login):
    analista = criar_analista()
    return analista, await login("paulo.ramos", "1234")


# ---------- unitarios (service) ----------

def test_service_gera_token_e_envia_por_email(banco, criar_analista, emails):
    analista = criar_analista()
    service = InvestidorService(InvestidorRepository(banco))
    investidor, erro = service.cadastrar_investidor(CadastroInvestidorEntrada(email=" Marina.Souza@Example.test "), analista.id_analista)

    assert erro is None
    assert investidor.email == "marina.souza@example.test"
    assert investidor.primeiro_acesso_concluido is False
    assert service.email_acesso_enviado is True
    assert emails[0]["para"] == "marina.souza@example.test"
    assert emails[0]["token"]


def test_service_email_em_branco_nao_gera(banco, criar_analista, emails):
    analista = criar_analista()
    investidor, erro = InvestidorService(InvestidorRepository(banco)).cadastrar_investidor(
        CadastroInvestidorEntrada(email="   "), analista.id_analista,
    )
    assert investidor is None
    assert erro == "O e-mail do investidor é obrigatório."
    assert emails == []


def test_service_falha_no_email_desfaz_o_cadastro(banco, criar_analista, monkeypatch):
    from app.shared import email_service

    def falhar(email, token):
        raise OSError("SMTP fora do ar")

    monkeypatch.setattr(email_service, "enviar_token_acesso", falhar)
    analista = criar_analista()
    with pytest.raises(OSError):
        InvestidorService(InvestidorRepository(banco)).cadastrar_investidor(
            CadastroInvestidorEntrada(email="marina.souza@example.test"), analista.id_analista,
        )
    assert InvestidorRepository(banco).buscar_usuario_por_email("marina.souza@example.test") is None


# ---------- API ----------

async def test_cenario1_geracao_de_token_bem_sucedida(cliente, analista_logado, emails):
    _, cabecalho = analista_logado
    resposta = await cliente.post("/investors", json={"email": "marina.souza@example.test"}, headers=cabecalho)

    assert resposta.status_code == 201
    assert resposta.json()["email_acesso_enviado"] is True
    assert resposta.json()["primeiro_acesso_concluido"] is False
    assert emails[0]["para"] == "marina.souza@example.test"

    # A senha temporaria enviada por e-mail libera o primeiro acesso (US 1.4).
    primeiro_acesso = await cliente.post("/auth/primeiro-acesso", json={
        "email": "marina.souza@example.test", "token": emails[0]["token"],
    })
    assert primeiro_acesso.status_code == 200


async def test_cenario2_email_em_branco(cliente, analista_logado, emails):
    _, cabecalho = analista_logado
    resposta = await cliente.post("/investors", json={"email": ""}, headers=cabecalho)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O e-mail do investidor é obrigatório."
    assert emails == []


async def test_cenario4_email_que_ja_possui_cadastro(cliente, analista_logado, criar_investidor, emails):
    _, cabecalho = analista_logado
    criar_investidor(email="marina.souza@email.com")
    resposta = await cliente.post("/investors", json={"email": "marina.souza@email.com"}, headers=cabecalho)
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Já existe um usuário com este e-mail."
    assert emails == []


async def test_sem_login_nao_gera_token(cliente, emails):
    resposta = await cliente.post("/investors", json={"email": "marina.souza@example.test"})
    assert resposta.status_code == 401
    assert emails == []
