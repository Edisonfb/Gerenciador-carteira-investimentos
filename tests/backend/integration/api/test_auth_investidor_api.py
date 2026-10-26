"""Item 1 - Autenticacao no Sistema (Investidor), pelos endpoints HTTP."""

from app.core.security import verificar_senha
from app.modules.investors.models import Investidor


SENHA = "Senha123"  # mesma senha das fixtures criar_analista/criar_investidor


async def test_login_do_investidor_retorna_token_bearer(cliente, criar_investidor):
    criar_investidor()

    resposta = await cliente.post(
        "/auth/login", json={"email": "investidor@teste.com", "senha": SENHA}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]


async def test_login_do_investidor_com_senha_errada_retorna_401(cliente, criar_investidor):
    criar_investidor()

    resposta = await cliente.post(
        "/auth/login", json={"email": "investidor@teste.com", "senha": "errada"}
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Email ou senha inválidos"


async def test_login_com_email_inexistente_retorna_401(cliente):
    resposta = await cliente.post(
        "/auth/login", json={"email": "ninguem@teste.com", "senha": SENHA}
    )

    assert resposta.status_code == 401


async def test_login_de_investidor_inativo_retorna_403(cliente, criar_investidor):
    criar_investidor(ativo=False)

    resposta = await cliente.post(
        "/auth/login", json={"email": "investidor@teste.com", "senha": SENHA}
    )

    assert resposta.status_code == 403


async def test_login_sem_campos_obrigatorios_retorna_422(cliente):
    resposta = await cliente.post("/auth/login", json={"email": "investidor@teste.com"})

    assert resposta.status_code == 422


async def test_auth_me_identifica_investidor_logado(cliente, criar_investidor, login):
    investidor = criar_investidor()
    cabecalho = await login("investidor@teste.com")

    resposta = await cliente.get("/auth/me", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id_usuario": investidor.id_usuario,
        "email": "investidor@teste.com",
        "tipo_usuario": "investidor",
        "ativo": True,
    }


async def test_auth_me_sem_token_retorna_401(cliente):
    resposta = await cliente.get("/auth/me")

    assert resposta.status_code == 401


async def test_auth_me_com_token_invalido_retorna_401(cliente):
    resposta = await cliente.get("/auth/me", headers={"Authorization": "Bearer invalido"})

    assert resposta.status_code == 401


async def test_token_para_de_valer_quando_investidor_e_desativado(
    cliente, sessao_banco, criar_investidor, login
):
    investidor = criar_investidor()
    cabecalho = await login("investidor@teste.com")
    investidor.ativo = False
    sessao_banco.commit()

    resposta = await cliente.get("/auth/me", headers=cabecalho)

    assert resposta.status_code == 401


async def test_investidor_acessa_o_proprio_perfil(cliente, criar_investidor, login):
    criar_investidor()
    cabecalho = await login("investidor@teste.com")

    resposta = await cliente.get("/investors/me", headers=cabecalho)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "investidor@teste.com"
    assert resposta.json()["tipo_usuario"] == "investidor"


async def test_analista_nao_acessa_rota_de_investidor(cliente, criar_analista, login):
    criar_analista()
    cabecalho = await login("analista@teste.com")

    resposta = await cliente.get("/investors/me", headers=cabecalho)

    assert resposta.status_code == 403


async def test_fluxo_completo_convite_e_primeiro_acesso(
    cliente, sessao_banco, criar_analista, login, emails_enviados
):
    criar_analista()
    cabecalho_analista = await login("analista@teste.com")

    convite = await cliente.post(
        "/investors", json={"email": "novo@teste.com"}, headers=cabecalho_analista
    )
    assert convite.status_code == 201
    assert convite.json()["primeiro_acesso_concluido"] is False
    [(_, token_inicial)] = emails_enviados

    cabecalho_investidor = await login("novo@teste.com", token_inicial)
    primeiro_acesso = await cliente.post(
        "/investors/me/first-access",
        json={"email_recuperacao": "recuperacao@teste.com", "nova_senha": "SenhaNova123"},
        headers=cabecalho_investidor,
    )
    assert primeiro_acesso.status_code == 200
    assert primeiro_acesso.json()["primeiro_acesso_concluido"] is True
    assert primeiro_acesso.json()["email_recuperacao"] == "recuperacao@teste.com"

    token_antigo = await cliente.post(
        "/auth/login", json={"email": "novo@teste.com", "senha": token_inicial}
    )
    assert token_antigo.status_code == 401
    await login("novo@teste.com", "SenhaNova123")

    investidor = sessao_banco.query(Investidor).filter_by(email="novo@teste.com").one()
    assert verificar_senha("SenhaNova123", investidor.senha_hash)


async def test_primeiro_acesso_nao_pode_ser_repetido(cliente, criar_investidor, login):
    criar_investidor(primeiro_acesso_concluido=True)
    cabecalho = await login("investidor@teste.com")

    resposta = await cliente.post(
        "/investors/me/first-access",
        json={"email_recuperacao": "recuperacao@teste.com", "nova_senha": "Outra123"},
        headers=cabecalho,
    )

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O primeiro acesso deste investidor já foi concluído."


async def test_primeiro_acesso_exige_token(cliente):
    resposta = await cliente.post(
        "/investors/me/first-access",
        json={"email_recuperacao": "recuperacao@teste.com", "nova_senha": "Outra123"},
    )

    assert resposta.status_code == 401
