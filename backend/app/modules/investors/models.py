"""Modelos persistidos do modulo de investidores."""

from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.modules.auth.models import Usuario
from app.db.enums import Tipo_Usuario

class Investidor(Usuario):
    __tablename__ = "investidor"

    id_investidor: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"))
    id_analista_responsavel: Mapped[int] = mapped_column(ForeignKey("analista.id_analista"))
    nome: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    sobrenome: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    rg: Mapped[Optional[str]] = mapped_column(String(10), unique=True, nullable=True)
    cpf: Mapped[Optional[str]] = mapped_column(String(11), unique=True, nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String(15), unique=True, nullable=True)
    cep: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    uf: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    cidade: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    bairro: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    logradouro: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    numero: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    email_recuperacao: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    primeiro_acesso_concluido: Mapped[bool] = mapped_column(default=False)
    
    analista_responsavel: Mapped["Analista"] = relationship(
        back_populates="investidores",
        foreign_keys="[Investidor.id_analista_responsavel]",)

    __mapper_args__ = {
        "polymorphic_identity": Tipo_Usuario.INVESTIDOR,
    }
    
    def __repr__(self) -> str:
        return f"Investidor(id={self.id_investidor!r}, nome={self.nome!r}, sobrenome={self.sobrenome!r}, rg={self.rg!r}, cpf={self.cpf!r}, telefone={self.telefone!r}, cep={self.cep!r}, uf={self.uf!r}, cidade={self.cidade!r}, bairro={self.bairro!r}, logradouro={self.logradouro!r}, numero={self.numero!r})"
