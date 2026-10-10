"""Modelos persistidos do modulo de carteiras."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Carteira(Base):
    """Representa uma carteira de investimentos de um investidor."""
    __tablename__ = "carteira"

    id_carteira: Mapped[int] = mapped_column(primary_key=True)
    id_investidor: Mapped[int] = mapped_column(ForeignKey("investidor.id_investidor"))

    nome: Mapped[str] = mapped_column(String(100))
    ativa: Mapped[bool] = mapped_column(Boolean, default = True) 
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    investidor = relationship("Investidor")