"""Valida o fluxo HTTP completo com SQLite isolado e email simulado."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import criar_token_acesso, verificar_senha
from app.core.config import settings
from app.db.enums import Tipo_Usuario
from app.modules.analysts.models import Analista
from app.modules.investors.models import Investidor


@pytest.fixture
def fluxo():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    from app.core.security import hash_senha
    with Session() as db:
        analista = Analista(email="analista@example.test", nome_usuario="analista", nome="Analista", senha_hash=hash_senha("senha-analista"), ativo=True)
        db.add(analista); db.commit(); db.refresh(analista)
        token_analista = criar_token_acesso(analista.id_usuario)
    def db_teste():
        with Session() as db:
            yield db
    anterior = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = db_teste
    try:
        with patch("app.modules.investors.service.email_service.enviar_token_acesso") as email:
            client = TestClient(app)
            resposta = client.post("/investors", headers={"Authorization": "Bearer " + token_analista}, json={"email": "convite@example.test"})
            assert resposta.status_code == 201, resposta.text
            assert resposta.json()["email_acesso_enviado"] is True
            email.assert_called_once()
            destino, token_convite = email.call_args.args
            assert destino == "convite@example.test"
            yield client, Session, token_convite, email
    finally:
        if anterior is None: app.dependency_overrides.pop(get_db, None)
        else: app.dependency_overrides[get_db] = anterior
        engine.dispose()


def obter_autorizacao(client, token_convite):
    resposta = client.post("/auth/primeiro-acesso", json={"email": " CONVITE@example.test ", "token": token_convite})
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["token_definicao"]


def cadastro(token):
    return {"token_definicao": token, "nome_usuario": " Ana ", "email_comunicacao": "comunicacao@example.test", "email_recuperacao": "recuperacao@example.test", "nova_senha": "nova-senha-segura"}


def test_convite_validacao_cadastro_login_e_recuperacao(fluxo):
    client, Session, token_convite, email = fluxo
    assert client.post("/auth/login", json={"email": "convite@example.test", "senha": token_convite}).status_code == 401
    token = obter_autorizacao(client, token_convite)
    assert client.get("/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 401
    assert client.post("/auth/redefinir-senha", json={"token": token, "senha": "outra-senha-segura"}).status_code == 400
    resposta = client.post("/investors/first-access", json=cadastro(token))
    assert resposta.status_code == 200, resposta.text
    assert "access_token" not in resposta.json()
    with Session() as db:
        investidor = db.query(Investidor).one()
        assert investidor.nome_usuario == "ana"
        assert investidor.email == "comunicacao@example.test"
        assert investidor.email_recuperacao == "recuperacao@example.test"
        assert investidor.primeiro_acesso_concluido is True
        assert verificar_senha("nova-senha-segura", investidor.senha_hash)
    assert client.post("/auth/login", json={"nome_usuario": "ana", "senha": "nova-senha-segura"}).status_code == 200
    assert client.post("/investors/first-access", json=cadastro(token)).status_code == 400
    assert client.post("/auth/primeiro-acesso", json={"email": "comunicacao@example.test", "token": token_convite}).status_code == 400
    email.assert_called_once()
    with patch("app.modules.auth.password_service.enviar_link_senha") as recuperar, patch.object(settings, "servidor_smtp", "smtp.example.test"), patch.object(settings, "email_remetente", "envio@example.test"):
        assert client.post("/auth/esqueci-senha", json={"email": "comunicacao@example.test"}).status_code == 200
        assert recuperar.call_args.args[0] == "recuperacao@example.test"


@pytest.mark.parametrize("situacao", ["expirado", "assinatura", "finalidade", "login"])
def test_autorizacao_invalida_nao_altera_cadastro(fluxo, situacao):
    client, Session, convite, _ = fluxo
    token = obter_autorizacao(client, convite)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    chave = settings.secret_key
    if situacao == "expirado": payload["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    if situacao == "assinatura": chave = "outra-chave-de-teste-com-tamanho-suficiente"
    if situacao == "finalidade": payload["purpose"] = "password_setup"
    token = criar_token_acesso(int(payload["sub"])) if situacao == "login" else jwt.encode(payload, chave, algorithm="HS256")
    assert client.post("/investors/first-access", json=cadastro(token)).status_code == 400
    with Session() as db:
        investidor = db.query(Investidor).one()
        assert investidor.email == "convite@example.test"
        assert investidor.nome_usuario is None
        assert not investidor.primeiro_acesso_concluido


@pytest.mark.parametrize("campo,valor", [("email_comunicacao", "invalido"), ("email_recuperacao", "comunicacao@example.test"), ("nova_senha", "curta"), ("nome_usuario", "   "), ("email_comunicacao", "analista@example.test"), ("nome_usuario", "analista")])
def test_dados_invalidos_nao_salvam_parcialmente_e_permite_corrigir(fluxo, campo, valor):
    client, Session, convite, _ = fluxo
    token = obter_autorizacao(client, convite)
    dados = {**cadastro(token), campo: valor}
    assert client.post("/investors/first-access", json=dados).status_code in (400, 422)
    with Session() as db:
        investidor = db.query(Investidor).one()
        assert investidor.email == "convite@example.test"
        assert not investidor.primeiro_acesso_concluido
    assert client.post("/investors/first-access", json=cadastro(token)).status_code == 200


@pytest.fixture
def conta_ativa(fluxo):
    client, Session, convite, _ = fluxo
    token = obter_autorizacao(client, convite)
    assert client.post("/investors/first-access", json=cadastro(token)).status_code == 200
    login = client.post("/auth/login", json={"nome_usuario": "ana", "senha": "nova-senha-segura"})
    return client, Session, {"Authorization": "Bearer " + login.json()["access_token"]}


def test_minha_conta_edita_dados_e_senha_juntos_sem_expor_segredos(conta_ativa):
    client, Session, headers = conta_ativa
    resposta = client.patch("/investors/me", headers=headers, json={"nome_usuario": " NovoUsuario ", "email": " novo@example.test ", "email_recuperacao": "nova-recuperacao@example.test", "senha_atual": "nova-senha-segura", "nova_senha": "senha-atualizada"})
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["nome_usuario"] == "novousuario"
    assert dados["email"] == "novo@example.test"
    assert dados["email_recuperacao"] == "nova-recuperacao@example.test"
    assert not {"senha_atual", "nova_senha", "senha_hash"}.intersection(dados)
    assert client.post("/auth/login", json={"nome_usuario": "novousuario", "senha": "senha-atualizada"}).status_code == 200
    assert client.post("/auth/login", json={"nome_usuario": "novousuario", "senha": "nova-senha-segura"}).status_code == 401
    with Session() as db:
        investidor = db.query(Investidor).one()
        assert investidor.primeiro_acesso_concluido is True


@pytest.mark.parametrize("nova_senha", [None, ""])
def test_minha_conta_preserva_senha_quando_nao_ha_nova(conta_ativa, nova_senha):
    client, _, headers = conta_ativa
    dados = {"nome_usuario": "ana", "email": "novo@example.test", "email_recuperacao": "recuperacao@example.test", "senha_atual": "nova-senha-segura"}
    if nova_senha is not None: dados["nova_senha"] = nova_senha
    assert client.patch("/investors/me", headers=headers, json=dados).status_code == 200
    assert client.post("/auth/login", json={"nome_usuario": "ana", "senha": "nova-senha-segura"}).status_code == 200


@pytest.mark.parametrize("alteracoes", [
    {"senha_atual": "errada"}, {"senha_atual": None}, {"nome_usuario": "analista"},
    {"email": "analista@example.test"}, {"email_recuperacao": "analista@example.test"},
    {"email": "invalido"}, {"email_recuperacao": "novo@example.test"},
    {"nova_senha": "curta"}, {"nova_senha": "á" * 37}, {"nome_usuario": None},
])
def test_minha_conta_rejeita_sem_alterar_nada(conta_ativa, alteracoes):
    client, Session, headers = conta_ativa
    dados = {"nome_usuario": "outrousuario", "email": "novo@example.test", "email_recuperacao": "recuperacao@example.test", "senha_atual": "nova-senha-segura", "nova_senha": "senha-atualizada", **alteracoes}
    resposta = client.patch("/investors/me", headers=headers, json=dados)
    assert resposta.status_code in (400, 422), resposta.text
    with Session() as db:
        investidor = db.query(Investidor).one()
        assert investidor.nome_usuario == "ana"
        assert investidor.email == "comunicacao@example.test"
        assert investidor.email_recuperacao == "recuperacao@example.test"
        assert verificar_senha("nova-senha-segura", investidor.senha_hash)


def test_minha_conta_exige_autenticacao_e_nao_aceita_outro_id(conta_ativa):
    client, _, headers = conta_ativa
    assert client.patch("/investors/me", json={"email": "novo@example.test"}).status_code == 401
    assert client.patch("/investors/me", headers=headers, json={"id_usuario": 1, "senha_atual": "nova-senha-segura"}).status_code == 422
