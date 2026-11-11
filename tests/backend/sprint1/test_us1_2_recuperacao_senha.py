"""US 1.2 - Recuperacao de senha (Esqueci minha senha)."""

from urllib.parse import parse_qs, urlparse

import pytest

from app.modules.auth.password_service import definir_senha
from app.modules.auth.repository import AuthRepository


def token_do_link(link):
    return parse_qs(urlparse(link).query)["token"][0]


async def test_cenario1_link_enviado_ao_email_de_recuperacao(cliente, criar_investidor, emails):
    investidor = criar_investidor()
    senha_antes = investidor.senha_hash

    resposta = await cliente.post("/auth/esqueci-senha", json={"email": "marina.souza@example.test"})

    assert resposta.status_code == 200
    assert "instruções" in resposta.json()["message"]
    assert len(emails) == 1
    assert emails[0]["para"] == "marina.souza2@example.test"  # e-mail de recuperacao
    assert "/definir-senha?token=" in emails[0]["link"]
    # A senha so muda quando o link for usado.
    login = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert login.status_code == 200
    assert investidor.senha_hash == senha_antes


async def test_cenario2_email_em_branco_nao_envia(cliente, criar_investidor, emails):
    criar_investidor()
    resposta = await cliente.post("/auth/esqueci-senha", json={"email": ""})
    assert resposta.status_code == 200
    assert emails == []


async def test_cenario3_email_nao_cadastrado_nao_envia(cliente, criar_investidor, emails):
    criar_investidor()
    resposta = await cliente.post("/auth/esqueci-senha", json={"email": "marina.souza23@example.test"})
    assert resposta.status_code == 200
    # A resposta e generica para nao revelar se o e-mail existe.
    assert "Se houver uma conta ativa elegível" in resposta.json()["message"]
    assert emails == []


async def test_cenario4_email_em_formato_invalido_nao_envia(cliente, criar_investidor, emails):
    criar_investidor()
    resposta = await cliente.post("/auth/esqueci-senha", json={"email": "marina.souza#example.test"})
    assert resposta.status_code == 200
    assert emails == []


async def test_cenario5_link_valido_redefine_a_senha(cliente, criar_investidor, emails):
    criar_investidor()
    await cliente.post("/auth/esqueci-senha", json={"email": "marina.souza@example.test"})
    token = token_do_link(emails[0]["link"])

    resposta = await cliente.post("/auth/redefinir-senha", json={"token": token, "senha": "NovaMarina@2025"})
    assert resposta.status_code == 200
    assert resposta.json()["message"] == "Senha definida com sucesso."

    nova = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "NovaMarina@2025"})
    antiga = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert nova.status_code == 200
    assert antiga.status_code == 401


async def test_link_nao_funciona_depois_da_troca_de_senha(cliente, criar_investidor, emails):
    criar_investidor()
    await cliente.post("/auth/esqueci-senha", json={"email": "marina.souza@example.test"})
    token = token_do_link(emails[0]["link"])
    await cliente.post("/auth/redefinir-senha", json={"token": token, "senha": "NovaMarina@2025"})

    segunda_vez = await cliente.post("/auth/redefinir-senha", json={"token": token, "senha": "OutraSenha@1"})
    assert segunda_vez.status_code == 400
    assert segunda_vez.json()["detail"] == "Link inválido ou expirado. Solicite um novo link."


async def test_link_invalido_e_recusado(cliente):
    resposta = await cliente.post("/auth/redefinir-senha", json={"token": "token-falso", "senha": "NovaMarina@2025"})
    assert resposta.status_code == 400


def test_service_nova_senha_curta_e_recusada(banco):
    with pytest.raises(ValueError, match="mínimo 8 caracteres"):
        definir_senha(AuthRepository(banco), "qualquer-token", "1234567")
