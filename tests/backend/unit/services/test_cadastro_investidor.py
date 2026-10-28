from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.enums import Tipo_Usuario
from app.core.dependencies import obter_usuario_autenticado
from app.core.config import settings
from app.modules.investors.schemas import CadastroInvestidorEntrada
from app.modules.investors.service import InvestidorService


DADOS = dict(nome="Teste", sobrenome="Cadastro", email="teste@example.test",
             cpf="12345678901", telefone="51999999999", cep="95700000", uf="RS",
             cidade="Cidade", bairro="Centro", logradouro="Rua", numero="10")


class Repository:
    def __init__(self):
        self.salvo = None

    def buscar_usuario_por_email(self, email):
        return None

    def buscar_investidor_por_cpf(self, cpf):
        return None

    def buscar_analista_por_usuario(self, id_usuario):
        assert id_usuario == 25
        return SimpleNamespace(id_analista=3)

    def salvar(self, investidor):
        investidor.id_investidor = 80
        investidor.id_usuario = 81
        self.salvo = investidor
        return investidor


@pytest.mark.parametrize("smtp", ["ausente", "falha", "sucesso"])
def test_cadastro_nao_falha_depois_de_salvar_por_causa_do_smtp(smtp):
    repository = Repository()
    service = InvestidorService(repository)
    with patch.object(settings, "servidor_smtp", "" if smtp == "ausente" else "smtp.example.test"), patch.object(settings, "email_remetente", "envio@example.test"), patch("app.modules.investors.service.email_service.enviar_token_acesso") as enviar:
        if smtp == "falha":
            enviar.side_effect = OSError("SMTP indisponível")
        investidor, erro = service.cadastrar_investidor(CadastroInvestidorEntrada(**DADOS, id_analista_responsavel=3))
    assert investidor is repository.salvo
    assert erro is None
    assert service.email_acesso_enviado == (smtp == "sucesso")
    if smtp == "ausente":
        enviar.assert_not_called()


@pytest.mark.parametrize("perfil", [Tipo_Usuario.ANALISTA, Tipo_Usuario.INVESTIDOR])
def test_rota_usa_analista_da_sessao_e_restringe_perfil(perfil):
    repository = Repository()
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[obter_usuario_autenticado] = lambda: SimpleNamespace(id_usuario=25, tipo_usuario=perfil)
    try:
        with patch("app.modules.investors.router.InvestidorRepository", return_value=repository), patch.object(settings, "servidor_smtp", ""):
            resposta = TestClient(app).post("/investors", json={**DADOS, "id_analista_responsavel": 999})
        assert resposta.status_code == (201 if perfil == Tipo_Usuario.ANALISTA else 403)
        if perfil == Tipo_Usuario.ANALISTA:
            assert repository.salvo.id_analista_responsavel == 3
            assert resposta.json()["email_acesso_enviado"] is False
        else:
            assert repository.salvo is None
    finally:
        app.dependency_overrides.clear()
