"""Acesso a dados do modulo de carteiras."""
from sqlalchemy.orm import Session

from app.modules.portfolios.models import Carteira

class CarteiraRepository:
    """Concentra as operações de banco para carteiras"""

    def __init__(self, db: Session ):
        self.db = db

    def adicionar(self, carteira: Carteira) -> Carteira:
        self.db.add(carteira)
        self.db.commit()
        self.db.refresh(carteira)
        return carteira

    def listar_por_investidor(self, id_investidor: int) -> list[Carteira]:
        return(
            self.db.query(Carteira)
            .filter(Carteira.id_investidor == id_investidor)
            .all()
        )

    def buscar_por_id_e_investidor(self, id_carteira: int, id_investidor: int,) -> Carteira | None:
        return (
            self.db.query(Carteira).filter(
                Carteira.id_carteira == id_carteira,
                Carteira.id_investidor == id_investidor
            )
            .first()
        )

    def atualizar(self, carteira: Carteira) -> Carteira:
        self.db.add(carteira)
        self.db.commit()
        self.db.refresh(carteira)
        return carteira

    def excluir(self, carteira: Carteira) -> None:
        self.db.delete(carteira)
        self.db.commit()