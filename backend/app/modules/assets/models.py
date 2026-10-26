"""Modelos persistidos do modulo de ativos financeiros."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Ativo(Base):
    """Representa um ativo para se rusado nas carteiras"""
    __tablename__ = "ativo"

    id_ativo: Mapped[int] = mapped_column(primary_key= True)
    codigo: Mapped[str] = mapped_column(String(10), unique = True, nullable= False)
    setor: Mapped[str] = mapped_column(String(80), nullable= False)
    ativo: Mapped[bool] = mapped_column(Boolean, default = True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    def __repr__(self):
        return (
            f"Ativo(id_ativo={self.id_ativo!r}, "
            f"codigo={self.codigo!r}, setor={self.setor!r}, ativo={self.ativo!r})"
        )