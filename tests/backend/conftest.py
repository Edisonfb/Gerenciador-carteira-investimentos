"""Fixtures dos testes do backend.

Banco falso: SQLite em memoria no lugar do MySQL (get_db sobrescrito).
E-mail falso: as funcoes de envio guardam as mensagens numa lista.
"""

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import hash_senha
from app.db.base import Base
from app.db.enums import Tipo_Usuario
from app.db.session import get_db
from app.main import app
from app.modules.analysts.models import Analista
from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.auth import password_service
from app.modules.investors.models import Investidor
from app.modules.portfolios.models import Carteira
from app.shared import email_service


# Ativos usados nas historias, com o setor do cadastro da B3.
CATALOGO = {
    "ABEV3": "Consumo não Cíclico",
    "BBDC3": "Financeiro",
    "BBDC4": "Financeiro",
    "CRFB3": "Consumo não Cíclico",
    "EGIE3": "Utilidade Pública",
    "ITUB3": "Financeiro",
    "ITUB4": "Financeiro",
    "AALR3": "Saúde",
}


@pytest.fixture
def banco():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db_falso():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_falso
    db = Sessao()
    for ticker, setor in CATALOGO.items():
        db.add(Ativo(ticker=ticker, setor=setor))
    db.commit()
    yield db
    db.close()
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
async def cliente(banco):
    transporte = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transporte, base_url="http://teste") as cliente:
        yield cliente


@pytest.fixture
def emails(monkeypatch):
    """Guarda os e-mails que seriam enviados, sem usar SMTP."""
    enviados = []
    monkeypatch.setattr(settings, "servidor_smtp", "smtp.falso")
    monkeypatch.setattr(settings, "email_remetente", "sistema@example.test")
    monkeypatch.setattr(
        email_service, "enviar_token_acesso",
        lambda email, token: enviados.append({"para": email, "token": token}),
    )
    monkeypatch.setattr(
        password_service, "enviar_link_senha",
        lambda email, link, primeiro_acesso=False: enviados.append({"para": email, "link": link}),
    )
    return enviados


@pytest.fixture
def criar_analista(banco):
    def _criar(nome_usuario="paulo.ramos", senha="1234", email="paulo.ramos@empresa.com.br", ativo=True):
        analista = Analista(
            email=email, nome_usuario=nome_usuario, senha_hash=hash_senha(senha),
            tipo_usuario=Tipo_Usuario.ANALISTA, nome="Paulo Ramos", ativo=ativo,
        )
        banco.add(analista)
        banco.commit()
        return analista

    return _criar


@pytest.fixture
def criar_investidor(banco, criar_analista):
    """Investidor com cadastro concluido (ja passou pelo primeiro acesso)."""
    def _criar(nome_usuario="marina.souza", senha="Marina@2025", email="marina.souza@example.test",
               email_recuperacao="marina.souza2@example.test", ativo=True):
        analista = banco.query(Analista).first() or criar_analista()
        investidor = Investidor(
            email=email, nome_usuario=nome_usuario, senha_hash=hash_senha(senha),
            email_recuperacao=email_recuperacao, tipo_usuario=Tipo_Usuario.INVESTIDOR,
            id_analista_responsavel=analista.id_analista,
            primeiro_acesso_concluido=True, ativo=ativo,
        )
        banco.add(investidor)
        banco.commit()
        return investidor

    return _criar


@pytest.fixture
def criar_convite(banco, criar_analista):
    """Investidor convidado pelo analista que ainda nao fez o primeiro acesso."""
    def _criar(email="marina.souza@example.test", senha_temporaria="eU6qTAwJi_A"):
        analista = banco.query(Analista).first() or criar_analista()
        investidor = Investidor(
            email=email, senha_hash=hash_senha(senha_temporaria),
            tipo_usuario=Tipo_Usuario.INVESTIDOR,
            id_analista_responsavel=analista.id_analista,
            primeiro_acesso_concluido=False, ativo=True,
        )
        banco.add(investidor)
        banco.commit()
        return investidor

    return _criar


@pytest.fixture
def login(cliente):
    async def _login(nome_usuario, senha):
        resposta = await cliente.post("/auth/login", json={"nome_usuario": nome_usuario, "senha": senha})
        assert resposta.status_code == 200, resposta.text
        return {"Authorization": f"Bearer {resposta.json()['access_token']}"}

    return _login


@pytest.fixture
async def investidor_logado(criar_investidor, login):
    """Cabecalho de autenticacao da investidora marina.souza."""
    criar_investidor()
    return await login("marina.souza", "Marina@2025")


@pytest.fixture
def criar_carteira(banco):
    """Cria a carteira direto no banco falso, com os ativos e objetivos informados."""
    def _criar(id_investidor, nome, ativos=None):
        carteira = Carteira(id_investidor=id_investidor, nome=nome)
        banco.add(carteira)
        banco.commit()
        for ticker, objetivo, *quantidade in (ativos or []):
            banco.add(AtivoCarteira(
                ticker=ticker, id_carteira=carteira.id_carteira,
                quantidade=quantidade[0] if quantidade else 0, objetivo_percentual=objetivo,
            ))
        banco.commit()
        return carteira

    return _criar
