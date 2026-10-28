"""Comando para recriar as tabelas do banco de desenvolvimento."""
import argparse
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_PROJETO))
sys.path.insert(0, str(RAIZ_PROJETO / "backend"))

from app.db.maintenance import GerenciadorBanco
from database.migrations.ativos import carregar_ativos, importar_ativos
from database.seeds.analista_teste import (
    EMAIL_ANALISTA_TESTE, USUARIO_ANALISTA_TESTE, criar_analista_teste,
)


def main(argumentos: list[str] | None = None) -> int:
    """Recria tabelas, cria o analista de teste e permite importar o catalogo."""
    parser = argparse.ArgumentParser(
        description=(
            "Apaga todas as tabelas e seus dados no banco configurado e recria "
            "a estrutura dos modelos atuais, com um analista de teste. O banco MySQL deve existir."
        ),
    )
    parser.add_argument(
        "--confirmar", action="store_true",
        help="Confirma a perda dos dados de todas as tabelas do banco configurado.",
    )
    parser.add_argument(
        "--popular-ativos", action="store_true",
        help="Importa o catalogo CSV de ativos depois de recriar as tabelas.",
    )
    opcoes = parser.parse_args(argumentos)
    if not opcoes.confirmar:
        parser.error("O reset apaga os dados. Use --confirmar para executar.")

    # Valida a entrada antes de qualquer exclusao quando houver populacao.
    if opcoes.popular_ativos:
        carregar_ativos()

    # A conexao de destino so e usada depois da confirmacao e da validacao do CSV.
    from app.db.session import engine

    print(f"Banco de destino: {engine.url.database or ':memory:'}")
    tabelas = GerenciadorBanco(engine).resetar(confirmar=True)
    print("Tabelas recriadas: " + ", ".join(tabelas))
    criar_analista_teste(engine)
    print(f"Analista de teste criado: {EMAIL_ANALISTA_TESTE} (usuário: {USUARIO_ANALISTA_TESTE})")
    if opcoes.popular_ativos:
        quantidade = importar_ativos(engine)
        print(f"Ativos importados: {quantidade}")
    print("O analista de teste já pode entrar na aplicação e cadastrar investidores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
