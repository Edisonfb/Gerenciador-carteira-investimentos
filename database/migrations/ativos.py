"""Importa o catalogo CSV de forma transacional e sem duplicar tickers."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import registrar_modelos
from app.modules.assets.models import Ativo
from app.modules.assets.schemas import CadastroAtivoEntrada

ARQUIVO_ATIVOS = Path(__file__).resolve().parents[1] / "seeds" / "ativos.csv"


def carregar_ativos(arquivo: Path = ARQUIVO_ATIVOS) -> list[CadastroAtivoEntrada]:
    """Valida o catalogo completo antes de qualquer alteracao no banco."""
    with Path(arquivo).open(encoding="utf-8-sig", newline="") as entrada:
        dados = [CadastroAtivoEntrada.model_validate(linha) for linha in csv.DictReader(entrada)]
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
