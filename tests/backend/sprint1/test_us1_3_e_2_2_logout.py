"""US 1.3 - Logout do investidor / US 2.2 - Logout do analista."""

from app.modules.auth.service import AuthService


def test_service_logout_retorna_mensagem(criar_investidor):
    investidor = criar_investidor()
    resposta = AuthService(repository=None).realizar_logout(investidor)
    assert resposta["mensagem"] == "Sessão de marina.souza@example.test encerrada com sucesso."


async def test_us1_3_cenario1_investidor_encerra_sessao(cliente, investidor_logado):
    resposta = await cliente.post("/auth/logout", headers=investidor_logado)
    assert resposta.status_code == 200
    assert "encerrada com sucesso" in resposta.json()["mensagem"]


async def test_us2_2_cenario1_analista_encerra_sessao(cliente, criar_analista, login):
    criar_analista()
    cabecalho = await login("paulo.ramos", "1234")
    resposta = await cliente.post("/auth/logout", headers=cabecalho)
    assert resposta.status_code == 200
    assert "encerrada com sucesso" in resposta.json()["mensagem"]


async def test_logout_sem_sessao_retorna_401(cliente):
    resposta = await cliente.post("/auth/logout")
    assert resposta.status_code == 401
