from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

import jwt
import pytest

from app.core.config import settings
from app.core.security import hash_senha, verificar_senha, ler_id_usuario_token
from app.modules.auth.password_service import solicitar_link, definir_senha, validar_primeiro_acesso


class Repository:
    def __init__(self):
        self.usuario = SimpleNamespace(id_usuario=7, email="conta@example.test", ativo=True,
                                       senha_hash=hash_senha("senha-inicial"), token_acesso="senha-inicial")
        self.salvo = False

    def buscar_por_email(self, email):
        return self.usuario if email == self.usuario.email else None

    def buscar_por_id(self, identificador):
        return self.usuario if identificador == self.usuario.id_usuario else None

    def salvar(self, usuario):
        self.salvo = True


def obter_link(repository, primeiro_acesso=False):
    with patch("app.modules.auth.password_service.enviar_link_senha") as enviar:
        solicitar_link(repository, repository.usuario.email, primeiro_acesso)
    enviar.assert_called_once()
    return parse_qs(urlparse(enviar.call_args.args[1]).query)["token"][0]


def test_senha_persistida_e_link_nao_reutilizavel():
    repository = Repository()
    token = obter_link(repository, True)
    definir_senha(repository, token, "nova-senha-segura")
    assert repository.salvo
    assert verificar_senha("nova-senha-segura", repository.usuario.senha_hash)
    assert repository.usuario.token_acesso == ""
    with pytest.raises(ValueError, match="inválido ou expirado"):
        definir_senha(repository, token, "outra-senha-segura")


def test_link_nao_permite_autenticacao():
    with pytest.raises(jwt.InvalidTokenError):
        ler_id_usuario_token(obter_link(Repository()))


@pytest.mark.parametrize("alteracao", ["expirado", "assinatura", "finalidade"])
def test_link_invalido_nao_altera_senha(alteracao):
    repository = Repository()
    token = obter_link(repository)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    chave = settings.secret_key
    if alteracao == "expirado":
        payload["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    elif alteracao == "assinatura":
        chave = "outra-chave-de-teste-com-32-caracteres"
    else:
        payload["purpose"] = "access"
    token = jwt.encode(payload, chave, algorithm="HS256")
    with pytest.raises(ValueError):
        definir_senha(repository, token, "nova-senha-segura")
    assert not repository.salvo


def test_conta_inexistente_inativa_e_primeiro_acesso_concluido_nao_enviam_email():
    repository = Repository()
    with patch("app.modules.auth.password_service.enviar_link_senha") as enviar:
        solicitar_link(repository, "inexistente@example.test", False)
        repository.usuario.ativo = False
        solicitar_link(repository, repository.usuario.email, False)
        repository.usuario.ativo = True
        repository.usuario.token_acesso = ""
        solicitar_link(repository, repository.usuario.email, True)
    enviar.assert_not_called()


def test_senha_curta_nao_salva():
    repository = Repository()
    with pytest.raises(ValueError, match="no mínimo 8"):
        definir_senha(repository, obter_link(repository), "curta")
    assert not repository.salvo


@pytest.mark.parametrize("caminho", ["/auth/esqueci-senha"])
def test_endpoint_indica_smtp_indisponivel(caminho):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.session import get_db

    def db_teste():
        yield None

    app.dependency_overrides[get_db] = db_teste
    try:
        with patch.object(settings, "servidor_smtp", ""):
            resposta = TestClient(app).post(caminho, json={"email": "conta@example.test"})
        assert resposta.status_code == 503
        assert "indisponível" in resposta.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_primeiro_acesso_valida_token_sem_enviar_email_e_libera_login_apos_senha():
    from app.modules.auth.service import AuthService
    repository = Repository()
    with patch("app.modules.auth.password_service.enviar_link_senha") as enviar:
        assert AuthService(repository).realizar_login(repository.usuario.email, "senha-inicial") is None
        token = validar_primeiro_acesso(repository, repository.usuario.email, "senha-inicial")
        with pytest.raises(jwt.InvalidTokenError):
            ler_id_usuario_token(token)
        definir_senha(repository, token, "nova-senha-definitiva")
        assert repository.usuario.token_acesso == ""
        assert AuthService(repository).realizar_login(repository.usuario.email, "senha-inicial") is None
        assert AuthService(repository).realizar_login(repository.usuario.email, "nova-senha-definitiva")["access_token"]
        with pytest.raises(ValueError):
            validar_primeiro_acesso(repository, repository.usuario.email, "senha-inicial")
    enviar.assert_not_called()


@pytest.mark.parametrize("situacao", ["email", "token", "inativo", "concluido", "unicode"])
def test_primeiro_acesso_rejeita_credenciais_invalidas(situacao):
    repository = Repository()
    email = repository.usuario.email
    token = "senha-inicial"
    if situacao == "email": email = "outro@example.test"
    if situacao == "token": token = "token-incorreto"
    if situacao == "inativo": repository.usuario.ativo = False
    if situacao == "concluido": repository.usuario.token_acesso = ""
    if situacao == "unicode": token = "token-inválido"
    with pytest.raises(ValueError, match="E-mail ou token inválido"):
        validar_primeiro_acesso(repository, email, token)
    assert not repository.salvo


def test_endpoints_primeiro_acesso_e_definicao_de_senha_sem_smtp():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.session import get_db
    repository = Repository()
    app.dependency_overrides[get_db] = lambda: None
    try:
        with patch("app.modules.auth.router.AuthRepository", return_value=repository), patch.object(settings, "servidor_smtp", ""), patch("app.modules.auth.password_service.enviar_link_senha") as enviar:
            client = TestClient(app)
            dados = {"email": repository.usuario.email, "token": "senha-inicial"}
            resposta = client.post("/auth/primeiro-acesso", json=dados)
            assert resposta.status_code == 200
            token = resposta.json()["token_definicao"]
            assert client.post("/auth/redefinir-senha", json={"token": token, "senha": "nova-senha-definitiva"}).status_code == 200
            assert client.post("/auth/primeiro-acesso", json=dados).status_code == 400
            assert client.post("/auth/redefinir-senha", json={"token": token, "senha": "outra-senha-definitiva"}).status_code == 400
        enviar.assert_not_called()
    finally:
        app.dependency_overrides.pop(get_db, None)
