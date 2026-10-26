"""Isola o módulo de ativos de falhas de inicialização em outros routers."""

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.enums import Tipo_Usuario
from app.db.session import get_db
from app.modules.analysts.models import Analista
from app.modules.assets.router import router
from app.modules.investors.models import Investidor


@pytest.fixture
def sessao_banco():
    """Cria as tabelas em memória sem conectar ao MySQL do usuário."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as sessao:
        yield sessao
    engine.dispose()


@pytest.fixture
async def cliente(sessao_banco):
    """Monta somente o router de ativos e substitui a conexão do banco."""
    app = FastAPI()
    app.include_router(router)

    def obter_banco_teste():
        """Compartilha a sessão entre a autenticação e os repositórios."""
        yield sessao_banco

    app.dependency_overrides[get_db] = obter_banco_teste
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://teste"
    ) as cliente:
        yield cliente
    app.dependency_overrides.clear()


@pytest.fixture
def criar_analista(sessao_banco):
    """Prepara o perfil utilizado para verificar a restrição de acesso."""
    def criar():
        """Persiste um analista ativo no banco de teste."""
        analista = Analista(
            email="analista@teste.com", senha_hash="hash-de-teste",
            tipo_usuario=Tipo_Usuario.ANALISTA, nome="Ana", ativo=True,
        )
        sessao_banco.add(analista)
        sessao_banco.commit()
        return analista

    return criar


@pytest.fixture
def criar_investidor(sessao_banco, criar_analista):
    """Prepara um investidor ativo para autenticação por token real."""
    def criar():
        """Persiste o investidor e seu analista responsável."""
        analista = criar_analista()
        investidor = Investidor(
            email="investidor@teste.com", senha_hash="hash-de-teste",
            tipo_usuario=Tipo_Usuario.INVESTIDOR,
            id_analista_responsavel=analista.id_analista,
            primeiro_acesso_concluido=True, ativo=True,
        )
        sessao_banco.add(investidor)
        sessao_banco.commit()
        return investidor

    return criar
