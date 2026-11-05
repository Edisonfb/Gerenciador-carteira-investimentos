"""Acesso a dados do modulo de cotacoes."""
from sqlalchemy.orm import Session

from app.modules.quotes.models import Cotacao


class CotacaoRepository:
    """Concentra as operacoes de banco das cotacoes."""

    def __init__(self, db: Session):
        self.db = db

    def buscar(self, ticker: str) -> Cotacao | None:
        return self.db.get(Cotacao, ticker)

    def salvar(self, cotacao: Cotacao) -> Cotacao:
        """Persiste a cotacao e desfaz a transacao em caso de falha."""
        try:
            self.db.add(cotacao)
            self.db.commit()
            self.db.refresh(cotacao)
            return cotacao
        except Exception:
            self.db.rollback()
            raise
