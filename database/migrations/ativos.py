import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import pandas
from app.db.session import engine

df = pandas.read_csv('..//database/seeds/ativos.csv')

ARQUIVO_ATIVOS = Path(__file__).resolve().parents[1] / "seeds" / "acoes-b3.csv"


def carregar_ativos(arquivo: Path = ARQUIVO_ATIVOS) -> list[CadastroAtivoEntrada]:
    """Valida o catalogo completo antes de qualquer alteracao no banco."""
    with Path(arquivo).open(encoding="utf-8-sig", newline="") as entrada:
        dados = [CadastroAtivoEntrada.model_validate(linha) for linha in csv.DictReader(entrada, delimiter=";")]
    tickers = [ativo.ticker for ativo in dados]
    if len(tickers) != len(set(tickers)):
        raise ValueError("O CSV possui tickers duplicados.")
    return dados


def importar_ativos(engine, arquivo: Path = ARQUIVO_ATIVOS) -> int:
    """Valida todo o CSV antes de gravar e preserva os ativos ja cadastrados."""
    registrar_modelos()
    dados = carregar_ativos(arquivo)
    with Session(engine) as sessao, sessao.begin():
        existentes = set(sessao.scalars(select(Ativo.ticker)).all())
        novos = [Ativo(**ativo.model_dump()) for ativo in dados if ativo.ticker not in existentes]
        sessao.add_all(novos)
        return len(novos)


if __name__ == "__main__":
    from app.db.session import engine
    print(f"Ativos importados: {importar_ativos(engine)}")
