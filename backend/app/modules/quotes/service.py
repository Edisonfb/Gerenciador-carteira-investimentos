"""Regras de negocio do modulo de cotacoes."""
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from app.modules.assets.repository import AtivoRepository
from app.modules.quotes.models import Cotacao
from app.modules.quotes.repository import CotacaoRepository
from app.shared import yahoo_finance


# Dentro desse tempo a cotacao salva no banco e usada sem consultar o Yahoo.
VALIDADE_COTACAO = timedelta(minutes=15)


class ErroCotacao(ValueError):
    """Representa uma falha prevista sem depender da camada HTTP."""

    def __init__(self, mensagem: str, status_code: int):
        super().__init__(mensagem)
        self.status_code = status_code


class CotacaoService:
    """Consulta o preco no Yahoo Finance e guarda o resultado no banco."""

    def __init__(self, repository: CotacaoRepository, ativos: AtivoRepository):
        self.repository = repository
        self.ativos = ativos

    def consultar_cotacao(self, ticker: str) -> Cotacao:
        ticker = ticker.strip().upper()
        if self.ativos.buscar_por_codigo(ticker) is None:
            raise ErroCotacao("Ativo não encontrado.", 404)

        cotacao = self.repository.buscar(ticker)
        agora = datetime.utcnow()
        if cotacao is not None and agora - cotacao.data_atualizacao < VALIDADE_COTACAO:
            return cotacao

        try:
            preco = yahoo_finance.buscar_preco(ticker)
        except RuntimeError:
            # Sem resposta do Yahoo, usa a ultima cotacao salva, se existir.
            if cotacao is not None:
                return cotacao
            raise ErroCotacao("Cotação indisponível no momento. Tente novamente mais tarde.", 503)

        if cotacao is None:
            cotacao = Cotacao(ticker=ticker)
        cotacao.preco = preco
        cotacao.data_atualizacao = agora
        try:
            return self.repository.salvar(cotacao)
        except IntegrityError:
            # Outra requisicao salvou a cotacao deste ativo ao mesmo tempo.
            return self.repository.buscar(ticker)
