"""Configuracao da sessao de banco de dados."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessao de banco para uso nas rotas e repositorios."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
