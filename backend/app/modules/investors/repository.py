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

    def buscar_por_usuario_id(self, id_usuario: int) -> Investidor | None:
        return (
            self.db.query(Investidor)
            .filter(Investidor.id_usuario == id_usuario)
            .first()
        )

    def adicionar(self, investidor: Investidor) -> Investidor:
        self.db.add(investidor)
        self.db.flush()
        self.db.refresh(investidor)
        return investidor

    def confirmar(self)-> None:
        self.db.commit()

    def desfazer(self) -> None:
        self.db.rollback()

    def atualizar(self, investidor: Investidor) -> Investidor:
        self.db.add(investidor)
        self.db.commit()
        self.db.refresh(investidor)
        return investidor