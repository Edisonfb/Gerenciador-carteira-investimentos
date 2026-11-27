"""Regras de negocio do modulo de carteiras."""
from decimal import Decimal

from app.modules.assets.repository import AtivoCarteiraRepository, AtivoRepository
from app.modules.portfolios.calculos import CalculosCarteira, PosicaoParaRebalanceamento
from app.modules.portfolios.models import Carteira
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.schemas import (
    CarteiraAtualizacaoEntrada, CarteiraCadastroEntrada,
    AtivoSimulacaoAporteSaida, CarteiraResumoSaida, PosicaoResumoSaida,
    SimulacaoAporteSaida,
)
from app.modules.quotes.service import CotacaoService, ErroCotacao


class ErroResumoCarteira(ValueError):
    """Indica carteira ausente ou cotacao que impede o resumo completo."""

    def __init__(self, mensagem: str, status_code: int):
        super().__init__(mensagem)
        self.status_code = status_code


class ErroSimulacaoAporte(ValueError):
    """Indica uma carteira ou cotação que impede sugerir compras."""

    def __init__(self, mensagem: str, status_code: int):
        super().__init__(mensagem)
        self.status_code = status_code

class ErroExclusaoCarteira(ValueError):
    """Impede excluir carteira que ainda tem ativos com quantidade."""

    def __init__(self, mensagem: str, status_code: int):
        super().__init__(mensagem)
        self.status_code = status_code


MENSAGEM_CARTEIRA_COM_QUANTIDADE = (
    "Você possui ativo(s) nessa carteira que possuem quantidade, faça registro de venda do(s) ativo(s)."
)


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
                if erro.status_code == 422:
                    raise ErroResumoCarteira(
                        f"Não foi possível calcular o patrimônio: o ativo {vinculo.ticker} não está em negociação.",
                        422,
                    ) from erro
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

    def simular_aporte(
        self, id_carteira: int, id_investidor: int, aporte: Decimal,
        vinculos: AtivoCarteiraRepository, ativos: AtivoRepository,
        cotacoes: CotacaoService,
        distribuicao: str = "balanceamento",
    ) -> SimulacaoAporteSaida:
        """Sugere compras em lotes de 100 para aproximar a carteira das metas."""
        carteira = self.buscar_carteira(id_carteira, id_investidor)
        if carteira is None:
            raise ErroSimulacaoAporte("Carteira não encontrada.", 404)
        if not carteira.ativa:
            raise ErroSimulacaoAporte("A carteira está desativada.", 400)

        vinculos_carteira = vinculos.listar_por_carteira(id_carteira)
        if not vinculos_carteira:
            raise ErroSimulacaoAporte("Inclua ativos na carteira antes de simular o aporte.", 400)

        posicoes = []
        cotacoes_usadas = {}
        for vinculo in vinculos_carteira:
            ativo = ativos.buscar_por_codigo(vinculo.ticker)
            if ativo is None or not ativo.ativo:
                raise ErroSimulacaoAporte(
                    f"O ativo {vinculo.ticker} está desativado e não pode receber sugestões de compra.",
                    400,
                )
            try:
                cotacao = cotacoes.consultar_cotacao(vinculo.ticker)
            except ErroCotacao as erro:
                if erro.status_code == 422:
                    raise ErroSimulacaoAporte(
                        f"Não foi possível simular o aporte: o ativo {vinculo.ticker} não está em negociação.",
                        422,
                    ) from erro
                raise ErroSimulacaoAporte(
                    f"Não foi possível simular o aporte: cotação de {vinculo.ticker} indisponível.",
                    503,
                ) from erro
            cotacoes_usadas[vinculo.ticker] = cotacao
            posicoes.append(PosicaoParaRebalanceamento(
                ticker=vinculo.ticker,
                quantidade=vinculo.quantidade,
                cotacao=cotacao.preco,
                objetivo_percentual=vinculo.objetivo_percentual,
            ))

        try:
            simulacao = CalculosCarteira.simular_rebalanceamento(posicoes, aporte, distribuicao)
        except ValueError as erro:
            raise ErroSimulacaoAporte(str(erro), 400) from erro

        posicoes_por_ticker = {posicao.ticker: posicao for posicao in posicoes}
        return SimulacaoAporteSaida(
            id_carteira=id_carteira,
            patrimonio_atual=simulacao.patrimonio_atual,
            aporte=simulacao.aporte,
            valor_investido=simulacao.valor_investido,
            saldo_restante=simulacao.saldo_restante,
            patrimonio_projetado=simulacao.patrimonio_projetado,
            aporte_minimo=simulacao.aporte_minimo,
            ativos=[
                AtivoSimulacaoAporteSaida(
                    **vars(projecao),
                    cotacao=cotacoes_usadas[projecao.ticker].preco,
                    data_atualizacao=cotacoes_usadas[projecao.ticker].data_atualizacao,
                    valor_atual=CalculosCarteira.valor_posicao(
                        posicoes_por_ticker[projecao.ticker].quantidade,
                        cotacoes_usadas[projecao.ticker].preco,
                    ),
                )
                for projecao in simulacao.ativos
            ],
        )

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

        # US 8.3 cenario 2.1: so exclui depois de vender todas as quantidades.
        if self.repository.possui_ativo_com_quantidade(id_carteira):
            raise ErroExclusaoCarteira(MENSAGEM_CARTEIRA_COM_QUANTIDADE, 400)

        self.repository.excluir(carteira)

        return True
