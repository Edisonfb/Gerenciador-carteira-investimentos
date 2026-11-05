"""Modelos persistidos do modulo de cotacoes."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Cotacao(Base):
    """Guarda a ultima cotacao consultada de cada ativo."""
    __tablename__ = "cotacao"

    ticker: Mapped[str] = mapped_column(ForeignKey("ativo.ticker"), primary_key=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"Cotacao(ticker={self.ticker!r}, preco={self.preco!r})"
