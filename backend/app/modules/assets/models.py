"""Modelos persistidos do modulo de ativos."""
from datetime import datetime
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.portfolios.models import Carteira


class Ativo(Base):
    """Representa o catalogo de ativos, identificado pelo ticker."""
    __tablename__ = "ativo"

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    codigo = synonym("ticker")
    nome: Mapped[str] = mapped_column(String(50), default="")
    setor: Mapped[str] = mapped_column(String(255))
    subsetor: Mapped[str] = mapped_column(String(255), default="")
    segmento: Mapped[str] = mapped_column(String(255), default="")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
    )

    ativos_carteira: Mapped[list["AtivoCarteira"]] = relationship(
        back_populates="ativo", foreign_keys="AtivoCarteira.ticker",
    )

    def __repr__(self) -> str:
        """Identifica o ativo nos registros de diagnostico."""
        return f"Ativo(ticker={self.ticker!r}, nome={self.nome!r})"


class AtivoCarteira(Base):
    """Relaciona um ativo a uma carteira com quantidade nao negativa."""
    __tablename__ = "ativo_carteira"
    __table_args__ = (
        CheckConstraint("quantidade >= 0", name="ck_ativo_carteira_quantidade_nao_negativa"),
    )

    ticker: Mapped[str] = mapped_column(ForeignKey("ativo.ticker"), primary_key=True)
    id_carteira: Mapped[int] = mapped_column(
        ForeignKey("carteira.id_carteira"), primary_key=True,
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)

    objetivo_percentual: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    ativo: Mapped["Ativo"] = relationship(
        back_populates="ativos_carteira", foreign_keys=[ticker],
    )
    carteira: Mapped["Carteira"] = relationship(
        back_populates="ativos_carteira", foreign_keys=[id_carteira],
    )

    def __repr__(self) -> str:
        """Identifica o vinculo e sua quantidade."""
        return (
            f"AtivoCarteira(ticker={self.ticker!r}, "
            f"id_carteira={self.id_carteira!r}, quantidade={self.quantidade!r})"
        )
