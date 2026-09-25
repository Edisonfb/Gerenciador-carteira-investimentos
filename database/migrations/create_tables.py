from app.db.base import Base
from app.db.session import engine

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

def create_tables():
    """Cria todas as tabelas no banco de dados."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()