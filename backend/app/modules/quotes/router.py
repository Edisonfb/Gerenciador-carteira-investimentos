"""Rotas HTTP do modulo de cotacoes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import exigir_investidor
from app.db.session import get_db
from app.modules.assets.repository import AtivoRepository
from app.modules.assets.schemas import Ticker
from app.modules.quotes.repository import CotacaoRepository
from app.modules.quotes.schemas import CotacaoSaida
from app.modules.quotes.service import CotacaoService, ErroCotacao


router = APIRouter(
    prefix="/quotes", tags=["quotes"], dependencies=[Depends(exigir_investidor)],
)


@router.get("/{ticker}", response_model=CotacaoSaida)
def consultar_cotacao(ticker: Ticker, db: Session = Depends(get_db)):
    """Retorna o preco atual do ativo, consultando o Yahoo Finance quando necessario."""
    service = CotacaoService(CotacaoRepository(db), AtivoRepository(db))
    try:
        return service.consultar_cotacao(ticker)
    except ErroCotacao as erro:
        raise HTTPException(status_code=erro.status_code, detail=str(erro)) from erro
