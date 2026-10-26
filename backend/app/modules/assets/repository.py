"""Acesso a dados do modulo de ativos financeiros."""
from sqlalchemy.orm import Session
from app.modules.assets.models import Ativo

class AtivoRepository:
    """Concentra as operações de banco para ativos financeiros."""

    def __init__(self, db: Session):
       self.db = db

    def adicionar(self, ativo: Ativo) -> Ativo:
        """Salva um novo ativo no banco de dados."""
        self.db.add(ativo)
        self.db.commit()
        self.db.refresh(ativo)
        return ativo

    def listar_todos(self) -> list[Ativo]:
        """Lista todos os ativos cadastrados"""
        return self.db.query(Ativo).order_by(Ativo.codigo).all()

    def buscar_por_id(self, id_ativo: int) -> Ativo | None:
        """Lista um ativo pelo id"""
        return self.db.query(Ativo).filter(Ativo.id_ativo == id_ativo).first()

    def buscar_por_codigo(self, codigo: str) -> Ativo | None:
        """Busca um ativo pelo codigo"""
        return self.db.query(Ativo).filter(Ativo.codigo == codigo).first()

    def atualizar(self, ativo: Ativo) -> Ativo:
        """Atualiza os dados de um ativo existente"""
        self.db.add(ativo)
        self.db.commit()
        self.db.refresh(ativo)
        return ativo

    def excluir(self, ativo: Ativo) -> None:
        """Remove um ativo do banco de dados"""
        self.db.delete(ativo)
        self.db.commit()