"""US 2.1 - Login do analista."""


async def test_cenario1_login_com_credenciais_validas(cliente, criar_analista):
    criar_analista()
    resposta = await cliente.post("/auth/login", json={"nome_usuario": "paulo.ramos", "senha": "1234"})
    assert resposta.status_code == 200

    token = resposta.json()["access_token"]
    eu = await cliente.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert eu.json()["tipo_usuario"] == "analista"


async def test_cenario2_login_com_senha_incorreta(cliente, criar_analista):
    criar_analista()
    resposta = await cliente.post("/auth/login", json={"nome_usuario": "paulo.ramos", "senha": "SenhaErrada1"})
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail, nome de usuário ou senha inválidos"


async def test_cenario3_analista_nao_gerencia_carteiras(cliente, criar_analista, login):
    criar_analista()
    cabecalho = await login("paulo.ramos", "1234")
    listar = await cliente.get("/portfolios", headers=cabecalho)
    criar = await cliente.post("/portfolios", json={"nome": "Aposentadoria"}, headers=cabecalho)
    assert listar.status_code == 403
    assert criar.status_code == 403
    assert listar.json()["detail"] == "Esta operação é permitida apenas para investidores."
