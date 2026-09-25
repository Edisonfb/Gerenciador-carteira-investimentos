from sqlalchemy.orm import Session
from app.modules.auth.models import Usuario


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def buscar_por_id(self, id_usuario: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    def salvar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario