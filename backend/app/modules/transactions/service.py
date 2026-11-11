"""Regras de negocio do modulo de transacoes."""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from app.modules.assets.repository import AtivoRepository
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.transactions.models import Transacao
from app.modules.transactions.repository import TransacaoRepository
from app.modules.transactions.schemas import TransacaoEntrada


LOTE_PADRAO = 100
QUANTIDADE_MAXIMA = 2147483647
VALOR_TOTAL_MAXIMO = Decimal("999999999999.99")


class ErroTransacao(ValueError):
    """Representa uma falha prevista sem depender da camada HTTP."""

    def __init__(self, mensagem: str, status_code: int):
        super().__init__(mensagem)
        self.status_code = status_code


class TransacaoService:
    """Registra compras e vendas e atualiza a quantidade do ativo na carteira."""

    def __init__(
        self, repository: TransacaoRepository, carteiras: CarteiraRepository,
        ativos: AtivoRepository,
    ):
        self.repository = repository
        self.carteiras = carteiras
        self.ativos = ativos

    def registrar_transacao(self, dados: TransacaoEntrada, id_investidor: int) -> Transacao:
        if dados.quantidade % LOTE_PADRAO != 0:
            raise ErroTransacao("A quantidade deve ser em lotes de 100 ações.", 400)

        carteira = self.carteiras.buscar_por_id_e_investidor(dados.id_carteira, id_investidor)
        if carteira is None:
            raise ErroTransacao("Carteira não encontrada.", 404)
        if not carteira.ativa:
            raise ErroTransacao("A carteira está desativada.", 400)

        ativo = self.ativos.buscar_por_codigo(dados.ticker)
        if ativo is None:
            raise ErroTransacao("Ativo não encontrado.", 404)
        if dados.tipo == "compra" and not ativo.ativo:
            raise ErroTransacao("O ativo está desativado.", 400)

        valor_total = dados.preco_unitario * dados.quantidade
        if valor_total > VALOR_TOTAL_MAXIMO:
            raise ErroTransacao("Valor total acima do limite permitido.", 400)
        agora = datetime.now(timezone.utc)
        data_transacao = dados.data_transacao or agora
        if data_transacao > agora:
            raise ErroTransacao("A data da transação não pode ser futura.", 400)

        ativo_carteira = self.repository.buscar_ativo_carteira_para_atualizacao(
            dados.ticker, dados.id_carteira,
        )
        if ativo_carteira is None:
            raise ErroTransacao("Ativo não encontrado nesta carteira.", 404)

        if dados.tipo == "compra":
            if ativo_carteira.quantidade + dados.quantidade > QUANTIDADE_MAXIMA:
                raise ErroTransacao("Quantidade acima do limite permitido.", 400)
            ativo_carteira.quantidade += dados.quantidade
        else:
            if dados.quantidade > ativo_carteira.quantidade:
                raise ErroTransacao(
                    "Quantidade insuficiente para venda. "
                    f"Você possui {ativo_carteira.quantidade} ações deste ativo.",
                    400,
                )
            ativo_carteira.quantidade -= dados.quantidade

        transacao = Transacao(
            id_investidor=id_investidor,
            id_carteira=carteira.id_carteira,
            nome_carteira=carteira.nome,
            ticker=dados.ticker,
            tipo=dados.tipo,
            quantidade=dados.quantidade,
            preco_unitario=dados.preco_unitario,
            valor_total=valor_total,
            data_transacao=data_transacao.astimezone(timezone.utc).replace(tzinfo=None),
        )
        try:
            return self.repository.salvar(transacao, ativo_carteira)
        except (IntegrityError, StaleDataError) as erro:
            raise ErroTransacao("Conflito ao registrar a transação. Tente novamente.", 409) from erro

    def listar_transacoes(
        self, id_investidor: int, id_carteira: int | None = None,
        ticker: str | None = None, tipo: str | None = None,
    ) -> list[Transacao]:
        if ticker is not None:
            ticker = ticker.strip().upper()
        return self.repository.listar_por_investidor(id_investidor, id_carteira, ticker, tipo)
