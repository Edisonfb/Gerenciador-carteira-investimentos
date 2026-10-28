from sqlalchemy.orm import Session
from app.modules.assets.models import Ativo, AtivoCarteira

class AtivoRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, ativo: Ativo) -> Ativo:
        self.db.add(ativo)
        self.db.commit()
        self.db.refresh(ativo)
        return ativo

    def listar_ativos(self) -> list[Ativo]:
        return self.db.query(Ativo).all()

class AtivoCarteiraRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, ativo_carteira: AtivoCarteira) -> AtivoCarteira:
        self.db.add(ativo_carteira)
        self.db.commit()
        self.db.refresh(ativo_carteira)
        return ativo_carteira

    def listar_por_carteira(self, id_carteira: int) -> list[AtivoCarteira]:
        return self.db.query(AtivoCarteira).filter(
            AtivoCarteira.id_carteira == id_carteira
        ).all()
