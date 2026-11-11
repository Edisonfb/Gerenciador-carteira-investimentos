"""Regras de negocio do modulo de carteiras."""
from decimal import Decimal

from app.modules.assets.repository import AtivoCarteiraRepository
from app.modules.portfolios.calculos import CalculosCarteira
from app.modules.portfolios.models import Carteira
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.schemas import (
    CarteiraAtualizacaoEntrada, CarteiraCadastroEntrada,
    CarteiraResumoSaida, PosicaoResumoSaida,
)
from app.modules.quotes.service import CotacaoService, ErroCotacao


class ErroResumoCarteira(ValueError):
    """Indica carteira ausente ou cotacao que impede o resumo completo."""

    def __init__(self, mensagem: str, status_code: int):
        super().__init__(mensagem)
        self.status_code = status_code

class CarteiraService:
    """Concentra as regras de negocio das carteiras."""
    def __init__(self, repository: CarteiraRepository):
        self.repository = repository

    def criar_carteira(self, dados: CarteiraCadastroEntrada, id_investidor: int
                       ) -> tuple[Carteira | None, str | None]:
        nome = dados.nome.strip()

        if not nome:
            return None, "O nome da carteira é obrigatório."

        carteira = Carteira(id_investidor = id_investidor, nome = nome)

        carteira_salva = self.repository.adicionar(carteira)

        return carteira_salva, None

    def listar_carteiras(self, id_investidor: int) -> list[Carteira]:
        return self.repository.listar_por_investidor(id_investidor)

    def buscar_carteira(self, id_carteira: int, id_investidor: int) -> Carteira | None:
        return self.repository.buscar_por_id_e_investidor(id_carteira, id_investidor)

    def calcular_resumo(
        self, id_carteira: int, id_investidor: int,
        vinculos: AtivoCarteiraRepository, cotacoes: CotacaoService,
    ) -> CarteiraResumoSaida:
        """Calcula patrimonio e participacoes apenas da carteira autorizada."""
        if self.buscar_carteira(id_carteira, id_investidor) is None:
            raise ErroResumoCarteira("Carteira não encontrada.", 404)

        posicoes = []
        for vinculo in vinculos.listar_por_carteira(id_carteira):
            if vinculo.quantidade == 0:
                posicoes.append(PosicaoResumoSaida(
                    ticker=vinculo.ticker, quantidade=0, cotacao=None,
                    data_atualizacao=None, valor_atual=Decimal("0.00"),
                    participacao_percentual=Decimal("0.00"),
                ))
                continue
            try:
                cotacao = cotacoes.consultar_cotacao(vinculo.ticker)
            except ErroCotacao as erro:
                raise ErroResumoCarteira(
                    f"Não foi possível calcular o patrimônio: cotação de {vinculo.ticker} indisponível.",
                    503,
                ) from erro
            posicoes.append(PosicaoResumoSaida(
                ticker=vinculo.ticker, quantidade=vinculo.quantidade,
                cotacao=cotacao.preco, data_atualizacao=cotacao.data_atualizacao,
                valor_atual=CalculosCarteira.valor_posicao(vinculo.quantidade, cotacao.preco),
                participacao_percentual=Decimal("0.00"),
            ))

        total = CalculosCarteira.patrimonio_total([posicao.valor_atual for posicao in posicoes])
        for posicao in posicoes:
            posicao.participacao_percentual = CalculosCarteira.participacao(posicao.valor_atual, total)
        return CarteiraResumoSaida(id_carteira=id_carteira, patrimonio_total=total, ativos=posicoes)

    def atualizar_carteira(self, id_carteira: int, id_investidor: int, dados: CarteiraAtualizacaoEntrada
                            ) -> tuple[Carteira |None, str | None]:
        carteira = self.repository.buscar_por_id_e_investidor(id_carteira, id_investidor)

        if carteira is None:
            return None, "Carteira não encontrada"

        atualizacoes = dados.model_dump(exclude_unset= True)

        if "nome" in atualizacoes:
            if atualizacoes["nome"] is None:
                 return None, "O nome da carteira é obrigatório."

            nome = atualizacoes["nome"].strip()

            if not nome:
                return None, "O nome da carteira é obrigatório."

            carteira.nome = nome

        if "ativa" in atualizacoes:
            if atualizacoes["ativa"] is None:
                return None, "O status da carteira é obrigatório."
            carteira.ativa = atualizacoes["ativa"]

        carteira_atualizada = self.repository.atualizar(carteira)

        return carteira_atualizada, None

    def excluir_carteira(self, id_carteira: int, id_investidor: int) -> bool:
        carteira = self.repository.buscar_por_id_e_investidor( id_carteira, id_investidor)

        if carteira is None:
            return False

        self.repository.excluir(carteira)

        return True
