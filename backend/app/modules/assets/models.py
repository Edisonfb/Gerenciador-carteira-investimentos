"""Modelos persistidos do modulo de ativos."""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.portfolios.models import Carteira


class Ativo(Base):
    __tablename__ = "ativo"

    ticker: Mapped[str] = mapped_column(String(6), primary_key=True)
    nome: Mapped[str] = mapped_column(String(50))
    setor: Mapped[str] = mapped_column(String(255))
    subsetor: Mapped[str] = mapped_column(String(255))
    segmento: Mapped[str] = mapped_column(String(255))

    ativos_carteira: Mapped[list["AtivoCarteira"]] = relationship(
        back_populates="ativo",
        foreign_keys="AtivoCarteira.ticker",
    )

    def __repr__(self) -> str:
        return f"Ativo(ticker={self.ticker!r}, nome={self.nome!r})"


class AtivoCarteira(Base):
    __tablename__ = "ativo_carteira"

    ticker: Mapped[str] = mapped_column(
        ForeignKey("ativo.ticker"), primary_key=True
    )
    id_carteira: Mapped[int] = mapped_column(
        ForeignKey("carteira.id_carteira"), primary_key=True
    )
    quantidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    ativo: Mapped["Ativo"] = relationship(
        back_populates="ativos_carteira",
        foreign_keys=[ticker],
    )
    carteira: Mapped["Carteira"] = relationship(
        back_populates="ativos_carteira",
        foreign_keys=[id_carteira],
    )

    def __repr__(self) -> str:
        return (
            f"AtivoCarteira(ticker={self.ticker!r}, "
            f"id_carteira={self.id_carteira!r}, "
            f"quantidade={self.quantidade!r})"
        )