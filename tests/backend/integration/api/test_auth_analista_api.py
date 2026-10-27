"""Item 2 - Autenticacao no Sistema (Analista), pelos endpoints HTTP.

US 2.1 - Login do analista e segregacao de perfil.
US 2.2 - Logout do analista.
"""


SENHA = "Senha123"  # mesma senha das fixtures criar_analista/criar_investidor


async def test_login_do_analista_retorna_token_bearer(cliente, criar_analista):
    criar_analista()

    resposta = await cliente.post(
        "/auth/login", json={"email": "analista@teste.com", "senha": SENHA}
    )

    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"
    assert resposta.json()["access_token"]


async def test_login_do_analista_com_senha_errada_retorna_401(cliente, criar_analista):
    criar_analista()

    resposta = await cliente.post(
        "/auth/login", json={"email": "analista@teste.com", "senha": "errada"}
    )

    assert resposta.status_code == 401


async def test_login_de_analista_inativo_retorna_403(cliente, criar_analista):
    criar_analista(ativo=False)

    resposta = await cliente.post(
        "/auth/login", json={"email": "analista@teste.com", "senha": SENHA}
    )

    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Usuário inativo. Contate o administrador."


async def test_auth_me_identifica_analista_logado(cliente, criar_analista, login):
    analista = criar_analista()
    cabecalho = await login("analista@teste.com")

    resposta = await cliente.get("/auth/me", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.json()["id_usuario"] == analista.id_usuario
    assert resposta.json()["tipo_usuario"] == "analista"


async def test_analista_logado_pode_cadastrar_investidor(
    cliente, criar_analista, login, emails_enviados
):
    criar_analista()
    cabecalho = await login("analista@teste.com")

    resposta = await cliente.post(
        "/investors", json={"email": "convidado@teste.com"}, headers=cabecalho
    )

    assert resposta.status_code == 201
    assert resposta.json()["email"] == "convidado@teste.com"
    assert [email for email, _ in emails_enviados] == ["convidado@teste.com"]


async def test_investidor_nao_acessa_rota_de_analista(
    cliente, criar_investidor, login, emails_enviados
):
    criar_investidor()
    cabecalho = await login("investidor@teste.com")

    resposta = await cliente.post(
        "/investors", json={"email": "convidado@teste.com"}, headers=cabecalho
    )

    assert resposta.status_code == 403
    assert emails_enviados == []


async def test_rota_de_analista_exige_token(cliente, emails_enviados):
    resposta = await cliente.post("/investors", json={"email": "convidado@teste.com"})

    assert resposta.status_code == 401
    assert emails_enviados == []


async def test_logout_do_analista(cliente, criar_analista, login):
    criar_analista()
    cabecalho = await login("analista@teste.com")

    resposta = await cliente.post("/auth/logout", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.json() == {
        "mensagem": "Sessão de analista@teste.com encerrada com sucesso."
    }


async def test_logout_sem_token_retorna_401(cliente):
    resposta = await cliente.post("/auth/logout")

    assert resposta.status_code == 401


async def test_logout_com_token_invalido_retorna_401(cliente):
    resposta = await cliente.post(
        "/auth/logout", headers={"Authorization": "Bearer invalido"}
    )

    assert resposta.status_code == 401
