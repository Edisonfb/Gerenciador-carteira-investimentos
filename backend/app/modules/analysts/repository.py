from sqlalchemy.orm import Session
from app.modules.analysts.models import Analista

class AnalistaRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Analista | None:
        return self.db.query(Analista).filter(Analista.email == email).first()

    def buscar_por_id(self, id_analista: int) -> Analista | None:
        return self.db.query(Analista).filter(Analista.id_analista == id_analista).first()

    def salvar(self, analista: Analista) -> Analista:
        self.db.add(analista)
        self.db.commit()
        self.db.refresh(analista)
        return analista