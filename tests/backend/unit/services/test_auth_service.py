"""Login e logout (AuthService), usados por investidor e analista.

Cobre:
- Item 1 - Autenticacao no Sistema (Investidor): login do investidor.
- Item 2 - Autenticacao no Sistema (Analista): US 2.1 login e US 2.2 logout.
"""

import pytest

from app.core.security import hash_senha, ler_id_usuario_token
from app.db.enums import Tipo_Usuario
from app.modules.analysts.models import Analista
from app.modules.auth.service import AuthService
from app.modules.investors.models import Investidor


SENHA = "senha-correta"
SENHA_HASH = hash_senha(SENHA)


class RepositorioAuthFalso:
    def __init__(self, usuarios):
        self.usuarios = {usuario.email: usuario for usuario in usuarios}

    def buscar_por_email(self, email):
        return self.usuarios.get(email)


def _analista(ativo=True):
    return Analista(
        id_usuario=1,
        email="analista@teste.com",
        senha_hash=SENHA_HASH,
        tipo_usuario=Tipo_Usuario.ANALISTA,
        nome="Ana",
        ativo=ativo,
    )


def _investidor(ativo=True):
    return Investidor(
        id_usuario=2,
        email="investidor@teste.com",
        senha_hash=SENHA_HASH,
        tipo_usuario=Tipo_Usuario.INVESTIDOR,
        id_analista_responsavel=1,
        ativo=ativo,
    )


@pytest.fixture
def service():
    return AuthService(RepositorioAuthFalso([_analista(), _investidor()]))


@pytest.mark.parametrize(
    "email, id_esperado",
    [("analista@teste.com", 1), ("investidor@teste.com", 2)],
)
def test_login_com_credenciais_corretas_retorna_token_do_usuario(service, email, id_esperado):
    resultado = service.realizar_login(email, SENHA)

    assert resultado["token_type"] == "bearer"
    assert ler_id_usuario_token(resultado["access_token"]) == id_esperado


@pytest.mark.parametrize("email", ["analista@teste.com", "investidor@teste.com"])
def test_login_com_senha_errada_retorna_none(service, email):
    assert service.realizar_login(email, "senha-errada") is None


def test_login_com_email_inexistente_retorna_none(service):
    assert service.realizar_login("ninguem@teste.com", SENHA) is None


@pytest.mark.parametrize("fabrica", [_analista, _investidor])
def test_login_de_usuario_inativo_retorna_false(fabrica):
    usuario = fabrica(ativo=False)
    service = AuthService(RepositorioAuthFalso([usuario]))

    assert service.realizar_login(usuario.email, SENHA) is False


def test_logout_retorna_mensagem_com_email_do_usuario(service):
    resultado = service.realizar_logout(_analista())

    assert resultado == {"mensagem": "Sessão de analista@teste.com encerrada com sucesso."}
