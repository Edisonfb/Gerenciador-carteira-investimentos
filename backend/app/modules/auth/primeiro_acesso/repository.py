"""Acesso aos dados do token de primeiro acesso."""

from sqlalchemy.orm import Session

from app.modules.auth.models import Analista
from app.modules.investors.models import Investidor


class PrimeiroAcessoRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_analista_por_usuario(self, id_usuario: int) -> Analista | None:
        return self.db.query(Analista).filter(Analista.id_usuario == id_usuario).first()

    def buscar_investidor(self, id_investidor: int) -> Investidor | None:
        return (
            self.db.query(Investidor)
            .filter(Investidor.id_investidor == id_investidor)
            .first()
        )

    def salvar(self, investidor: Investidor) -> Investidor:
        self.db.add(investidor)
        self.db.commit()
        self.db.refresh(investidor)
        return investidor
