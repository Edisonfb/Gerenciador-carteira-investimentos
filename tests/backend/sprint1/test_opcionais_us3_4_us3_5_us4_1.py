"""Historias opcionais (amarelo) da Sprint 1 que ja existem no backend.

US 3.4 - Exclusao de conta de investidor
US 3.5 - Edicao da propria conta pelo investidor
US 4.1 - Cadastro de conta de analista
"""


# ---------- US 3.4 ----------

async def test_us3_4_cenario1_conta_excluida_nao_autentica(cliente, criar_investidor):
    investidor = criar_investidor()
    resposta = await cliente.delete(f"/investors/{investidor.id_investidor}")
    assert resposta.status_code == 204

    login = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert login.status_code == 401


async def test_us3_4_excluir_investidor_inexistente(cliente):
    resposta = await cliente.delete("/investors/999")
    assert resposta.status_code == 404


# ---------- US 3.5 ----------

def dados_conta(**alteracoes):
    dados = {
        "nome_usuario": "marina.souza", "email": "marina.souza@example.test",
        "email_recuperacao": "marina.souza2@example.test", "senha_atual": "Marina@2025",
    }
    dados.update(alteracoes)
    return dados


async def test_us3_5_cenario1_altera_email_de_recuperacao(cliente, investidor_logado, emails):
    resposta = await cliente.patch("/investors/me", headers=investidor_logado,
                                   json=dados_conta(email_recuperacao="marina.recovery2@email.com"))
    assert resposta.status_code == 200
    assert resposta.json()["email_recuperacao"] == "marina.recovery2@email.com"

    # O novo e-mail passa a ser usado na recuperacao de senha (US 1.2).
    await cliente.post("/auth/esqueci-senha", json={"email": "marina.souza@example.test"})
    assert emails[0]["para"] == "marina.recovery2@email.com"


async def test_us3_5_cenario2_altera_a_senha(cliente, investidor_logado):
    resposta = await cliente.patch("/investors/me", headers=investidor_logado, json=dados_conta(nova_senha="Marina#Nova1"))
    assert resposta.status_code == 200

    nova = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina#Nova1"})
    assert nova.status_code == 200


async def test_us3_5_senha_atual_errada_nao_salva(cliente, investidor_logado):
    resposta = await cliente.patch("/investors/me", headers=investidor_logado,
                                   json=dados_conta(senha_atual="errada", nova_senha="Marina#Nova1"))
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Senha atual inválida. Confira a senha para confirmar as alterações."


async def test_us3_5_cenario3_email_de_outra_conta(cliente, criar_investidor, login):
    criar_investidor(nome_usuario="carlos.lima", email="carlos.lima@email.com", email_recuperacao="carlos2@email.com")
    criar_investidor()
    cabecalho = await login("marina.souza", "Marina@2025")

    resposta = await cliente.patch("/investors/me", headers=cabecalho, json=dados_conta(email="carlos.lima@email.com"))
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Um dos e-mails informados já está em uso por outra conta."


# ---------- US 4.1 ----------

async def test_us4_1_cenario1_cadastro_de_analista_permite_login(cliente, banco):
    resposta = await cliente.post("/analysts", json={
        "nome": "Paulo Ramos", "email": "paulo.ramos@empresa.com.br", "nome_usuario": "paulo.ramos", "senha": "Senha@123",
    })
    assert resposta.status_code == 201

    login = await cliente.post("/auth/login", json={"email": "paulo.ramos@empresa.com.br", "senha": "Senha@123"})
    assert login.status_code == 200


async def test_us4_1_cenario4_email_ja_existente(cliente, criar_analista):
    criar_analista()
    resposta = await cliente.post("/analysts", json={
        "nome": "Paulo Ramos", "email": "paulo.ramos@empresa.com.br", "nome_usuario": "paulo2", "senha": "Senha@123",
    })
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Já existe um usuário com este e-mail."
