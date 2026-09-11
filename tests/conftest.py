"""Fixtures compartilhadas de toda a pasta tests/."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.db.base import Base
from app.main import app
from app.modules.assets import models as assets_models  # noqa: F401
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.investors import models as investors_models  # noqa: F401
from app.modules.portfolios import models as portfolios_models  # noqa: F401
from app.modules.transactions import models as transactions_models  # noqa: F401


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """Ativa FKs no SQLite usado pelos testes."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db() -> Session:
    """Cria um banco SQLite limpo para cada teste."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session) -> TestClient:
    """Cliente HTTP da API com sessao de teste injetada."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(client: TestClient) -> tuple[TestClient, dict[str, str]]:
    """Registra um usuario e devolve o client com header Authorization."""
    email = "e2e@example.com"
    password = "senha123"
    client.post(
        "/auth/register",
        json={"name": "E2E User", "email": email, "password": password},
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return client, headers
