"""US 3.1 - Cadastro do investidor via link de convite."""

import pytest

from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import PrimeiroAcessoInvestidorEntrada
from app.modules.investors.service import InvestidorService

CADASTRO = {
    "nome_usuario": "marina.souza",
    "email_comunicacao": "marina.souza@example.test",
    "email_recuperacao": "marina.souza2@example.test",
    "nova_senha": "Marina@2025",
}


@pytest.fixture
def autorizacao(cliente, criar_convite):
    """Faz o primeiro acesso (US 1.4) e devolve o token que libera o Cadastro."""
    async def _autorizacao(email="marina.souza@example.test"):
        criar_convite(email=email)
        resposta = await cliente.post("/auth/primeiro-acesso", json={"email": email, "token": "eU6qTAwJi_A"})
        return resposta.json()["token_definicao"]

    return _autorizacao


# ---------- unitarios (service) ----------

def test_service_recuperacao_igual_a_comunicacao_e_recusada(banco, criar_convite):
    convidado = criar_convite()
    dados = PrimeiroAcessoInvestidorEntrada(
        nome_usuario="marina.souza", email_recuperacao="marina.souza@example.test", nova_senha="Marina@2025",
    )
    investidor, erro = InvestidorService(InvestidorRepository(banco)).concluir_primeiro_acesso(convidado.id_usuario, dados)
    assert investidor is None
    assert erro == "O e-mail de recuperação deve ser diferente do e-mail principal."


def test_service_cadastro_normaliza_usuario(banco, criar_convite):
    convidado = criar_convite()
    dados = PrimeiroAcessoInvestidorEntrada(
        nome_usuario="  Marina.Souza ", email_recuperacao="marina.souza2@example.test", nova_senha="Marina@2025",
    )
    investidor, erro = InvestidorService(InvestidorRepository(banco)).concluir_primeiro_acesso(convidado.id_usuario, dados)
    assert erro is None
    assert investidor.nome_usuario == "marina.souza"
    assert investidor.primeiro_acesso_concluido is True


# ---------- API ----------

async def test_cenario1_cadastro_bem_sucedido(cliente, autorizacao):
    token = await autorizacao()
    resposta = await cliente.post("/investors/first-access", json={"token_definicao": token, **CADASTRO})
    assert resposta.status_code == 200
    assert resposta.json()["message"] == "Cadastro concluído com sucesso. Entre com seu usuário e senha."

    login = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert login.status_code == 200


async def test_cenario2_email_de_recuperacao_em_branco(cliente, autorizacao):
    token = await autorizacao()
    resposta = await cliente.post("/investors/first-access", json={"token_definicao": token, **CADASTRO, "email_recuperacao": ""})
    assert resposta.status_code == 422

    login = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert login.status_code == 401  # cadastro nao foi concluido


async def test_cenario3_usuario_de_login_ja_existente(cliente, criar_investidor, autorizacao):
    criar_investidor(email="outra@example.test", email_recuperacao="outra2@example.test")  # ja usa "marina.souza"
    token = await autorizacao(email="ana.maria@example.test")
    resposta = await cliente.post("/investors/first-access", json={
        "token_definicao": token, **CADASTRO,
        "email_comunicacao": "ana.maria@example.test", "email_recuperacao": "ana.maria2@example.test",
    })
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Já existe um usuário com este nome de usuário."


async def test_cenario4_email_de_comunicacao_ja_cadastrado(cliente, criar_investidor, autorizacao):
    criar_investidor(nome_usuario="outra", email="marina.souza@email.com", email_recuperacao="outra2@example.test")
    token = await autorizacao()
    resposta = await cliente.post("/investors/first-access", json={
        "token_definicao": token, **CADASTRO, "email_comunicacao": "marina.souza@email.com",
    })
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Já existe um usuário com este e-mail de comunicação."


async def test_cenario4_email_de_recuperacao_ja_cadastrado(cliente, criar_investidor, autorizacao):
    criar_investidor(nome_usuario="outra", email="outra@example.test", email_recuperacao="marina.souza2@example.test")
    token = await autorizacao(email="ana.maria@example.test")
    resposta = await cliente.post("/investors/first-access", json={
        "token_definicao": token, **CADASTRO, "nome_usuario": "ana.maria", "email_comunicacao": "ana.maria@example.test",
    })
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Este e-mail de recuperação já está em uso."


async def test_cenario5_email_em_formato_invalido(cliente, autorizacao):
    token = await autorizacao()
    resposta = await cliente.post("/investors/first-access", json={
        "token_definicao": token, **CADASTRO, "email_comunicacao": "marina.souza#example.test",
    })
    assert resposta.status_code == 422


async def test_sem_autorizacao_valida_nao_cadastra(cliente, criar_convite):
    criar_convite()
    resposta = await cliente.post("/investors/first-access", json={"token_definicao": "token-falso", **CADASTRO})
    assert resposta.status_code == 400
