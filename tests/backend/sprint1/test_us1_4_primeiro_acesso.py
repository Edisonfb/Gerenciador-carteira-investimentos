"""US 1.4 - Primeiro acesso do investidor."""

import pytest

from app.modules.auth.password_service import validar_primeiro_acesso
from app.modules.auth.repository import AuthRepository

MENSAGEM_INVALIDO = "E-mail ou token inválido, ou primeiro acesso já concluído."


# ---------- unitarios (service) ----------

def test_service_token_correto_gera_autorizacao_de_cadastro(banco, criar_convite):
    criar_convite()
    autorizacao = validar_primeiro_acesso(AuthRepository(banco), "marina.souza@example.test", "eU6qTAwJi_A")
    assert isinstance(autorizacao, str) and autorizacao


def test_service_token_errado_gera_erro(banco, criar_convite):
    criar_convite()
    with pytest.raises(ValueError, match="E-mail ou token inválido"):
        validar_primeiro_acesso(AuthRepository(banco), "marina.souza@example.test", "Temp#0000")


# ---------- API ----------

async def test_cenario2_primeiro_acesso_bem_sucedido(cliente, criar_convite):
    criar_convite()
    resposta = await cliente.post("/auth/primeiro-acesso", json={"email": "marina.souza@example.test", "token": "eU6qTAwJi_A"})
    assert resposta.status_code == 200
    assert resposta.json()["token_definicao"]  # libera a tela de Cadastro (US 3.1)


async def test_cenario3_campos_obrigatorios_em_branco(cliente, criar_convite):
    criar_convite()
    sem_token = await cliente.post("/auth/primeiro-acesso", json={"email": "marina.souza@example.test", "token": ""})
    sem_email = await cliente.post("/auth/primeiro-acesso", json={"email": "", "token": "eU6qTAwJi_A"})
    assert sem_token.status_code == 422
    assert sem_email.status_code == 422


async def test_cenario4_senha_temporaria_incorreta(cliente, criar_convite):
    criar_convite()
    resposta = await cliente.post("/auth/primeiro-acesso", json={"email": "marina.souza@example.test", "token": "Temp#0000"})
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == MENSAGEM_INVALIDO


async def test_cenario5_email_diferente_do_convite(cliente, criar_convite):
    criar_convite()
    resposta = await cliente.post("/auth/primeiro-acesso", json={"email": "marina.souzaa@example.test", "token": "eU6qTAwJi_A"})
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == MENSAGEM_INVALIDO


async def test_cenario6_email_em_formato_invalido(cliente, criar_convite):
    criar_convite()
    resposta = await cliente.post("/auth/primeiro-acesso", json={"email": "marina.souza#email", "token": "eU6qTAwJi_A"})
    assert resposta.status_code == 400
    assert "token_definicao" not in resposta.json()


async def test_cenario7_acesso_ja_utilizado(cliente, criar_investidor):
    # Cadastro ja concluido: o convite nao pode ser usado de novo.
    criar_investidor(senha="Temp#4821")
    resposta = await cliente.post("/auth/primeiro-acesso", json={"email": "marina.souza@example.test", "token": "Temp#4821"})
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == MENSAGEM_INVALIDO


async def test_cenario8_senha_temporaria_nao_faz_login(cliente, criar_convite):
    criar_convite()
    resposta = await cliente.post("/auth/login", json={"email": "marina.souza@example.test", "senha": "eU6qTAwJi_A"})
    assert resposta.status_code == 401
    assert "access_token" not in resposta.json()
