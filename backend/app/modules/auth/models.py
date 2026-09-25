"""Modelos persistidos do modulo de autenticacao."""

from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.enums import Tipo_Usuario
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    tipo_usuario: Mapped[Tipo_Usuario] = mapped_column(SQLEnum(Tipo_Usuario))
    data_cadastro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        "polymorphic_on": tipo_usuario
    }

    def __repr__(self) -> str:
        return f"Usuario(id={self.id_usuario!r}, email={self.email!r}, tipo_usuario={self.tipo_usuario!r}, data_cadastro={self.data_cadastro!r})"

class Analista(Usuario):
    __tablename__ = "analista"

    id_analista: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"))
    nome: Mapped[str] = mapped_column(String(50))

    investidores: Mapped[List["Investidor"]] = relationship(back_populates="analista_responsavel")

    __mapper_args__ = {
        "polymorphic_identity": Tipo_Usuario.ANALISTA,
    }

    def __repr__(self) -> str:
        return f"Analista(id={self.id_analista!r}, nome={self.nome!r})"