"""Modelos persistidos do modulo de carteiras."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.investors.models import Investidor
    from app.modules.assets.models import AtivoCarteira


class Carteira(Base):
    """Representa uma carteira de investimentos de um investidor."""
    __tablename__ = "carteira"

    id_carteira: Mapped[int] = mapped_column(primary_key=True)
    id_investidor: Mapped[int] = mapped_column(
        ForeignKey("investidor.id_investidor"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    investidor: Mapped["Investidor"] = relationship(
        back_populates="carteiras",
    )

    ativos_carteira: Mapped[list["AtivoCarteira"]] = relationship(
        back_populates="carteira",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Carteira(id={self.id_carteira!r}, nome={self.nome!r})"