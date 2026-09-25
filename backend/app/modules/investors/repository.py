"""Acesso a dados do modulo de investidores."""
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario
from app.modules.investors.models import Investidor

class InvestidorRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_usuario_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def buscar_investidor_por_cpf(self, cpf: str) -> Investidor | None:
        return self.db.query(Investidor).filter(Investidor.cpf == cpf).first()

    def salvar(self, investidor: Investidor) -> Investidor:
        self.db.add(investidor)
        self.db.commit()
        self.db.refresh(investidor)
        return investidor