"""Modelos persistidos do modulo de investidores."""

from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.auth.models import Usuario
from app.db.enums import Tipo_Usuario

class Investidor(Usuario):
    __tablename__ = "investidor"

    id_investidor: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"))
    id_analista_responsavel: Mapped[int] = mapped_column(ForeignKey("analista.id_analista"))
    nome: Mapped[str] = mapped_column(String(30))
    sobrenome: Mapped[str] = mapped_column(String(30))
    rg: Mapped[Optional[str]] = mapped_column(String(10), unique=True, nullable=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    telefone: Mapped[str] = mapped_column(String(15), unique=True)
    cep: Mapped[str] = mapped_column(String(8))
    uf: Mapped[str] = mapped_column(String(2))
    cidade: Mapped[str] = mapped_column(String(32))
    bairro: Mapped[str] = mapped_column(String(30))
    logradouro: Mapped[str] = mapped_column(String(50))
    numero: Mapped[str] = mapped_column(String(5))
    token_acesso: Mapped[str] = mapped_column(String(255))
    
    analista_responsavel: Mapped["Analista"] = relationship(
        back_populates="investidores",
        foreign_keys="[Investidor.id_analista_responsavel]",)

    __mapper_args__ = {
        "polymorphic_identity": Tipo_Usuario.INVESTIDOR,
    }
    
    def __repr__(self) -> str:
        return f"Investidor(id={self.id_investidor!r}, nome={self.nome!r}, sobrenome={self.sobrenome!r}, rg={self.rg!r}, cpf={self.cpf!r}, telefone={self.telefone!r}, cep={self.cep!r}, uf={self.uf!r}, cidade={self.cidade!r}, bairro={self.bairro!r}, logradouro={self.logradouro!r}, numero={self.numero!r})"