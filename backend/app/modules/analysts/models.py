from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.db.enums import Tipo_Usuario
from datetime import datetime
from app.modules.auth.models import Usuario

class Analista(Usuario):
    __tablename__ = "analista"

    id_analista: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"))
    nome: Mapped[str] = mapped_column(String(50))

    investidores: Mapped[List["Investidor"]] = relationship(
        back_populates="analista_responsavel",
        foreign_keys="[Investidor.id_analista_responsavel]",
        )

    __mapper_args__ = {
        "polymorphic_identity": Tipo_Usuario.ANALISTA,
    }

    def __repr__(self) -> str:
        return f"Analista(id={self.id_analista!r}, nome={self.nome!r})"