"""Modelos persistidos do modulo de transacoes."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Transacao(Base):
    """Registra uma compra ou venda de ativo em uma carteira."""
    __tablename__ = "transacao"
    __table_args__ = (
        CheckConstraint("tipo IN ('compra', 'venda')", name="ck_transacao_tipo"),
        CheckConstraint("quantidade > 0", name="ck_transacao_quantidade_positiva"),
    )

    id_transacao: Mapped[int] = mapped_column(primary_key=True)
    id_investidor: Mapped[int] = mapped_column(
        ForeignKey("investidor.id_investidor"), nullable=False,
    )
    # Se a carteira for excluida, o historico permanece com o nome guardado abaixo.
    id_carteira: Mapped[int | None] = mapped_column(
        ForeignKey("carteira.id_carteira", ondelete="SET NULL"), nullable=True,
    )
    nome_carteira: Mapped[str] = mapped_column(String(100), nullable=False)
    ticker: Mapped[str] = mapped_column(ForeignKey("ativo.ticker"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    data_transacao: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"Transacao(id={self.id_transacao!r}, tipo={self.tipo!r}, "
            f"ticker={self.ticker!r}, quantidade={self.quantidade!r})"
        )
