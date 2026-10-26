"""Fixtures dos testes de API: app real com banco SQLite em memoria."""

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_senha
from app.db.base import Base
from app.db.enums import Tipo_Usuario
from app.db.session import get_db
from app.main import app
from app.modules.analysts.models import Analista
from app.modules.investors.models import Investidor
from app.shared import email_service


SENHA = "Senha123"


@pytest.fixture
def sessao_banco():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessaoTeste = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db_teste():
        db = SessaoTeste()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_teste
    db = SessaoTeste()
    yield db
    db.close()
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
async def cliente(sessao_banco):
    transporte = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transporte, base_url="http://teste") as cliente:
        yield cliente


@pytest.fixture
def emails_enviados(monkeypatch):
    enviados = []
    monkeypatch.setattr(
        email_service,
        "enviar_token_acesso",
        lambda email, token: enviados.append((email, token)),
    )
    return enviados


@pytest.fixture
def criar_analista(sessao_banco):
    def _criar(email="analista@teste.com", ativo=True):
        analista = Analista(
            email=email,
            senha_hash=hash_senha(SENHA),
            tipo_usuario=Tipo_Usuario.ANALISTA,
            nome="Ana",
            ativo=ativo,
        )
        sessao_banco.add(analista)
        sessao_banco.commit()
        return analista

    return _criar


@pytest.fixture
def criar_investidor(sessao_banco, criar_analista):
    def _criar(email="investidor@teste.com", ativo=True, primeiro_acesso_concluido=True):
        analista = (
            sessao_banco.query(Analista).first() or criar_analista()
        )
        investidor = Investidor(
            email=email,
            senha_hash=hash_senha(SENHA),
            tipo_usuario=Tipo_Usuario.INVESTIDOR,
            id_analista_responsavel=analista.id_analista,
            primeiro_acesso_concluido=primeiro_acesso_concluido,
            ativo=ativo,
        )
        sessao_banco.add(investidor)
        sessao_banco.commit()
        return investidor

    return _criar


@pytest.fixture
def login(cliente):
    async def _login(email, senha=SENHA):
        resposta = await cliente.post("/auth/login", json={"email": email, "senha": senha})
        assert resposta.status_code == 200, resposta.text
        return {"Authorization": f"Bearer {resposta.json()['access_token']}"}

    return _login
