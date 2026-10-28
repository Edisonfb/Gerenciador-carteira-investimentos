"""Comando explicito para apagar as tabelas do banco configurado."""
import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.db.maintenance import GerenciadorBanco


def drop_tables(*, confirmar: bool = False) -> None:
    """Delega a exclusao ao gerenciador, exigindo confirmacao explicita."""
    from app.db.session import engine
    GerenciadorBanco(engine).apagar_tabelas(confirmar=confirmar)


def main(argumentos: list[str] | None = None) -> int:
    """Exige a opcao --confirmar antes de remover dados."""
    parser = argparse.ArgumentParser(description="Apaga todas as tabelas do banco configurado.")
    parser.add_argument("--confirmar", action="store_true", help="Confirma a exclusão dos dados.")
    opcoes = parser.parse_args(argumentos)
    if not opcoes.confirmar:
        parser.error("A exclusão apaga os dados. Use --confirmar para executar.")
    drop_tables(confirmar=True)
    print("Tabelas removidas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
