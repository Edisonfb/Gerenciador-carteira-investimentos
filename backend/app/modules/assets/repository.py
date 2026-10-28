"""Acesso a dados dos ativos e seus vinculos com carteiras."""
from sqlalchemy.orm import Session

from app.modules.assets.models import Ativo, AtivoCarteira


class AtivoRepository:
    """Concentra consultas e persistencia do catalogo."""

    def __init__(self, db: Session):
        """Recebe a sessao compartilhada da requisicao."""
        self.db = db

    def salvar(self, ativo: Ativo) -> Ativo:
        """Persiste o ativo e desfaz a transacao em caso de falha."""
        try:
            self.db.add(ativo)
            self.db.commit()
            self.db.refresh(ativo)
            return ativo
        except Exception:
            self.db.rollback()
            raise

    adicionar = salvar
    atualizar = salvar

    def listar_ativos(self) -> list[Ativo]:
        """Lista o catalogo em ordem de ticker."""
        return self.db.query(Ativo).order_by(Ativo.ticker).all()

    listar_todos = listar_ativos

    def buscar_por_codigo(self, codigo: str) -> Ativo | None:
        """Consulta o ticker exato, mantendo o nome anterior do metodo."""
        return self.db.get(Ativo, codigo)

    def buscar_por_setor(self, setor: str) -> list[Ativo]:
        """Recupera a consulta por setor da branch backup."""
        return (
            self.db.query(Ativo).filter(Ativo.setor == setor)
            .order_by(Ativo.ticker).all()
        )

    def excluir(self, ativo: Ativo) -> None:
        """Exclui um ativo e desfaz a transacao caso haja referencias impeditivas."""
        try:
            self.db.delete(ativo)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise


class AtivoCarteiraRepository:
    """Persiste os vinculos entre ativos e carteiras."""

    def __init__(self, db: Session):
        """Recebe a sessao compartilhada da requisicao."""
        self.db = db

    def salvar(self, ativo_carteira: AtivoCarteira) -> AtivoCarteira:
        """Persiste o vinculo e restaura a sessao apos falha."""
        try:
            self.db.add(ativo_carteira)
            self.db.commit()
            self.db.refresh(ativo_carteira)
            return ativo_carteira
        except Exception:
            self.db.rollback()
            raise

    def buscar(self, ticker: str, id_carteira: int) -> AtivoCarteira | None:
        """Busca a chave composta, inclusive para detectar duplicidade."""
        return self.db.get(AtivoCarteira, (ticker, id_carteira))

    def excluir(self, ativo_carteira: AtivoCarteira) -> None:
        """Remove apenas o vinculo da carteira e desfaz a transacao se falhar."""
        try:
            self.db.delete(ativo_carteira)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def listar_por_carteira(self, id_carteira: int) -> list[AtivoCarteira]:
        """Lista os ativos da carteira previamente autorizada pelo servico."""
        return (
            self.db.query(AtivoCarteira)
            .filter(AtivoCarteira.id_carteira == id_carteira)
            .order_by(AtivoCarteira.ticker).all()
        )
