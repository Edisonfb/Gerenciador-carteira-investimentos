from sqlalchemy.orm import Session
from app.modules.auth.models import Usuario
from app.modules.analysts.models import Analista

class AnalistaRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Analista | None:
        return self.db.query(Analista).filter(Analista.email == email).first()

    def buscar_usuario_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def buscar_usuario_por_nome_usuario(self, nome_usuario: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.nome_usuario == nome_usuario).first()

    def buscar_por_id(self, id_analista: int) -> Analista | None:
        return self.db.query(Analista).filter(Analista.id_analista == id_analista).first()

    def salvar(self, analista: Analista) -> Analista:
        self.db.add(analista)
        self.db.commit()
        self.db.refresh(analista)
        return analista

    def listar_todos(self) -> list[Analista]:
        return self.db.query(Analista).all()

    def buscar_por_usuario_id(self, id_usuario: int) -> Analista | None:
        return self.db.query(Analista).filter(Analista.id_usuario == id_usuario).first()
