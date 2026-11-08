"""Cria tabelas ausentes conforme os modelos atuais, sem apagar dados."""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.maintenance import GerenciadorBanco


def create_tables() -> list[str]:
    """Mantem o comando existente usando o gerenciador central de estrutura."""
    from app.db.session import engine
    return GerenciadorBanco(engine).criar_tabelas()


if __name__ == "__main__":
    print("Tabelas registradas: " + ", ".join(create_tables()))
