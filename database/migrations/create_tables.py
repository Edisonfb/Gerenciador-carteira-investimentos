import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db import Base
from app.db.session import engine
from app.modules.analysts.models import Analista
from app.modules.auth.models import Usuario
from app.modules.investors.models import Investidor
from app.modules.portfolios.models import Carteira
from app.modules.assets.models import Ativo


def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
