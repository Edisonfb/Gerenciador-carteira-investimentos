"""Acesso a dados do modulo de transacoes."""
from sqlalchemy.orm import Session

from app.modules.assets.models import AtivoCarteira
from app.modules.transactions.models import Transacao


class TransacaoRepository:
    """Concentra as operacoes de banco das transacoes."""

    def __init__(self, db: Session):
        self.db = db
        self.em_lote = False

    def iniciar_lote(self) -> None:
        """Adia o commit ate todas as compras serem validadas e gravadas."""
        self.em_lote = True

    def concluir_lote(self) -> None:
        """Confirma todas as compras em uma unica transacao do banco."""
        self.db.commit()
        self.em_lote = False

    def desfazer_lote(self) -> None:
        """Desfaz todas as compras caso qualquer item falhe."""
        self.db.rollback()
        self.em_lote = False

    def buscar_ativo_carteira_para_atualizacao(
        self, ticker: str, id_carteira: int,
    ) -> AtivoCarteira | None:
        """Bloqueia a linha do ativo na carteira para impedir duas vendas ao mesmo tempo."""
        return (
            self.db.query(AtivoCarteira)
            .filter(AtivoCarteira.ticker == ticker, AtivoCarteira.id_carteira == id_carteira)
            .populate_existing().with_for_update().first()
        )

    def salvar(self, transacao: Transacao, ativo_carteira: AtivoCarteira) -> Transacao:
        """Grava a transacao e a nova quantidade juntas; se algo falhar, desfaz as duas."""
        try:
            self.db.add(transacao)
            self.db.add(ativo_carteira)
            if self.em_lote:
                self.db.flush()
            else:
                self.db.commit()
            self.db.refresh(transacao)
            return transacao
        except Exception:
            self.db.rollback()
            raise

    def listar_por_investidor(
        self, id_investidor: int, id_carteira: int | None = None,
        ticker: str | None = None, tipo: str | None = None,
    ) -> list[Transacao]:
        """Lista as transacoes do investidor, das mais recentes para as mais antigas."""
        consulta = self.db.query(Transacao).filter(Transacao.id_investidor == id_investidor)
        if id_carteira is not None:
            consulta = consulta.filter(Transacao.id_carteira == id_carteira)
        if ticker is not None:
            consulta = consulta.filter(Transacao.ticker == ticker)
        if tipo is not None:
            consulta = consulta.filter(Transacao.tipo == tipo)
        return consulta.order_by(
            Transacao.data_transacao.desc(), Transacao.id_transacao.desc(),
        ).all()
