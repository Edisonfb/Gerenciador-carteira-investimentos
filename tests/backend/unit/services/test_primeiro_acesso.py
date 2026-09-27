"""Testes unitários do envio do token de primeiro acesso."""

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db
from app.main import app
from app.modules.auth.primeiro_acesso.email import FalhaEnvioEmail
from app.modules.auth.primeiro_acesso.service import PrimeiroAcessoService


class RepositorioFalso:
    def __init__(self, investidor):
        self.investidor = investidor
        self.salvamentos = 0

    def buscar_investidor(self, id_investidor):
        return self.investidor

    def salvar(self, investidor):
        self.salvamentos += 1
        return investidor


def investidor_exemplo():
    return SimpleNamespace(
        email="ana@email.com",
        nome="Ana",
        token_acesso="token-antigo",
        token_expira_em=None,
        token_utilizado=True,
    )


def test_retorna_erro_quando_investidor_nao_existe():
    service = PrimeiroAcessoService(RepositorioFalso(None))

    mensagem, erro = service.enviar_token(1)

    assert mensagem is None
    assert erro == "Investidor não encontrado."


def test_retorna_erro_quando_email_e_invalido():
    investidor = investidor_exemplo()
    investidor.email = "sem-arroba"
    repositorio = RepositorioFalso(investidor)
    service = PrimeiroAcessoService(repositorio)

    mensagem, erro = service.enviar_token(1)

    assert mensagem is None
    assert erro == "Investidor não possui um e-mail válido."
    assert repositorio.salvamentos == 0


def test_grava_token_e_envia_link(monkeypatch):
    investidor = investidor_exemplo()
    repositorio = RepositorioFalso(investidor)
    links_enviados = []

    def falso_envio(destinatario, nome, link):
        links_enviados.append((destinatario, nome, link))

    monkeypatch.setattr(
        "app.modules.auth.primeiro_acesso.service.enviar_link_primeiro_acesso",
        falso_envio,
    )
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:5173")

    mensagem, erro = PrimeiroAcessoService(repositorio).enviar_token(1)

    assert erro is None
    assert mensagem == "Token de primeiro acesso enviado para o e-mail do investidor."
    assert investidor.token_acesso != "token-antigo"
    assert investidor.token_utilizado is False
    assert investidor.token_expira_em > datetime.utcnow() + timedelta(hours=23)
    assert links_enviados == [
        (
            "ana@email.com",
            "Ana",
            f"http://localhost:5173/primeiro-acesso?token={investidor.token_acesso}",
        )
    ]


def test_desfaz_token_quando_o_email_falha(monkeypatch):
    investidor = investidor_exemplo()
    repositorio = RepositorioFalso(investidor)

    def falha_envio(destinatario, nome, link):
        raise FalhaEnvioEmail("falha")

    monkeypatch.setattr(
        "app.modules.auth.primeiro_acesso.service.enviar_link_primeiro_acesso",
        falha_envio,
    )

    mensagem, erro = PrimeiroAcessoService(repositorio).enviar_token(1)

    assert mensagem is None
    assert erro == "Não foi possível enviar o token para o e-mail do investidor."
    assert investidor.token_acesso == "token-antigo"
    assert investidor.token_utilizado is True
    assert repositorio.salvamentos == 2


@pytest.fixture
def api_sem_banco():
    def banco_falso():
        yield None

    app.dependency_overrides[get_db] = banco_falso
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_rota_sem_analista_autenticado_retorna_401(api_sem_banco):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as cliente:
        resposta = await cliente.post(
            "/auth/primeiro-acesso/enviar",
            json={"id_investidor": 1},
        )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Analista não autenticado."
