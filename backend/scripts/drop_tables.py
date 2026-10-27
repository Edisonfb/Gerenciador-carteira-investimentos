# backend/scripts/drop_tables.py
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base
from app.db.session import engine


def drop_tables():
    """Remove todas as tabelas do banco de dados."""
    print("Tabelas no metadata:", list(Base.metadata.tables.keys()))
    Base.metadata.drop_all(bind=engine)
    print("Tabelas removidas com sucesso.")


if __name__ == "__main__":
    drop_tables()