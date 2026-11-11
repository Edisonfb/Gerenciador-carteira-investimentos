"""Calculos financeiros reutilizaveis para posicoes de carteiras."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP


CENTAVO = Decimal("0.01")
LOTE_COMPRA = 100


@dataclass(frozen=True)
class PosicaoParaRebalanceamento:
    """Dados de uma posicao e sua meta para simular compras."""

    ticker: str
    quantidade: int
    cotacao: Decimal
    objetivo_percentual: Decimal


@dataclass(frozen=True)
class ProjecaoAtivo:
    """Mostra a compra sugerida e a distancia projetada da meta."""

    ticker: str
    objetivo_percentual: Decimal
    quantidade_atual: int
    participacao_atual: Decimal
    distancia_atual: Decimal
    quantidade_sugerida: int
    custo_sugerido: Decimal
    quantidade_projetada: int
    valor_projetado: Decimal
    participacao_projetada: Decimal
    distancia_projetada: Decimal


@dataclass(frozen=True)
class SimulacaoRebalanceamento:
    """Agrupa o investimento simulado, o saldo e as posicoes projetadas."""

    patrimonio_atual: Decimal
    aporte: Decimal
    valor_investido: Decimal
    saldo_restante: Decimal
    patrimonio_projetado: Decimal
    ativos: list[ProjecaoAtivo]


class CalculosCarteira:
    """Reune calculos puros de posicao, patrimonio e participacao."""

    @staticmethod
    def redistribuir_objetivos(
        objetivos_atuais: dict[str, Decimal], novo_ticker: str, novo_objetivo: Decimal,
    ) -> dict[str, Decimal]:
        """Reserva a meta nova e reduz as antigas mantendo suas proporcoes."""
        if not novo_ticker or novo_ticker in objetivos_atuais:
            raise ValueError("O novo ticker deve ser válido e ainda não estar na carteira.")
        if (not novo_objetivo.is_finite() or novo_objetivo <= 0 or novo_objetivo > 100
                or novo_objetivo != novo_objetivo.quantize(CENTAVO)):
            raise ValueError("O novo objetivo deve estar entre 0,01% e 100%.")
        if not objetivos_atuais:
            if novo_objetivo != 100:
                raise ValueError("O primeiro ativo deve receber 100% do objetivo.")
            return {novo_ticker: Decimal("100.00")}
        if novo_objetivo == 100:
            raise ValueError("A nova meta deve deixar percentual para os ativos existentes.")
        if any(
            not ticker or not meta.is_finite() or meta <= 0 or meta > 100
            or meta != meta.quantize(CENTAVO)
            for ticker, meta in objetivos_atuais.items()
        ) or sum(objetivos_atuais.values(), Decimal(0)) != 100:
            raise ValueError("Os objetivos atuais devem ser positivos e somar 100%.")

        restante = Decimal(100) - novo_objetivo
        # Em centesimos de percentual, a meta exata antiga e meta * restante.
        exatos = {ticker: meta * restante for ticker, meta in objetivos_atuais.items()}
        centesimos = {
            ticker: int(exato.to_integral_value(rounding=ROUND_DOWN))
            for ticker, exato in exatos.items()
        }
        faltantes = int(restante * 100) - sum(centesimos.values())
        ordem = sorted(exatos, key=lambda ticker: (-(exatos[ticker] - centesimos[ticker]), ticker))
        for ticker in ordem[:faltantes]:
            centesimos[ticker] += 1
        if any(valor == 0 for valor in centesimos.values()):
            raise ValueError("A nova meta deixaria algum ativo com objetivo de 0%.")
        return {
            **{ticker: Decimal(centesimos[ticker]) / 100 for ticker in objetivos_atuais},
            novo_ticker: novo_objetivo,
        }

    @staticmethod
    def valor_posicao(quantidade: int, preco_unitario: Decimal) -> Decimal:
        """Calcula o valor atual de uma posicao em reais."""
        return (Decimal(quantidade) * preco_unitario).quantize(CENTAVO)

    @staticmethod
    def patrimonio_total(valores: list[Decimal]) -> Decimal:
        """Soma os valores atuais de todas as posicoes da carteira."""
        return sum(valores, Decimal("0.00"))

    @staticmethod
    def participacao(valor_posicao: Decimal, patrimonio_total: Decimal) -> Decimal:
        """Retorna a participacao percentual, inclusive sem patrimonio."""
        if patrimonio_total == 0:
            return Decimal("0.00")
        return (valor_posicao * 100 / patrimonio_total).quantize(CENTAVO, rounding=ROUND_HALF_UP)

    @staticmethod
    def simular_rebalanceamento(
        posicoes: list[PosicaoParaRebalanceamento], aporte: Decimal,
    ) -> SimulacaoRebalanceamento:
        """Sugere lotes de compra que aproximam a carteira das metas sem alterar dados."""
        if not aporte.is_finite() or aporte < 0 or aporte != aporte.quantize(CENTAVO):
            raise ValueError("O aporte deve ser um valor não negativo em centavos.")

        tickers = set()
        for posicao in posicoes:
            if not posicao.ticker or posicao.ticker in tickers:
                raise ValueError("Os tickers da carteira devem ser únicos e válidos.")
            tickers.add(posicao.ticker)
            if isinstance(posicao.quantidade, bool) or not isinstance(posicao.quantidade, int) or posicao.quantidade < 0:
                raise ValueError("A quantidade atual deve ser um inteiro não negativo.")
            if (not posicao.cotacao.is_finite() or posicao.cotacao <= 0
                    or posicao.cotacao != posicao.cotacao.quantize(CENTAVO)):
                raise ValueError(f"Cotação inválida para {posicao.ticker}.")
            meta = posicao.objetivo_percentual
            if not meta.is_finite() or meta < 0 or meta > 100 or meta != meta.quantize(CENTAVO):
                raise ValueError(f"Objetivo inválido para {posicao.ticker}.")
        if posicoes and sum((p.objetivo_percentual for p in posicoes), Decimal(0)) != 100:
            raise ValueError("A soma dos objetivos deve ser 100%.")

        valores = {p.ticker: CalculosCarteira.valor_posicao(p.quantidade, p.cotacao) for p in posicoes}
        patrimonio_atual = CalculosCarteira.patrimonio_total(list(valores.values()))
        patrimonio_planejado = patrimonio_atual + aporte
        sugestoes = {p.ticker: 0 for p in posicoes}
        saldo = aporte

        # A cada rodada, escolhe o lote que mais reduz a soma dos desvios
        # quadrados em reais em relacao ao patrimonio apos todo o aporte.
        while True:
            melhor_ticker = None
            melhor_melhoria = Decimal(0)
            melhor_custo = Decimal(0)
            for posicao in sorted(posicoes, key=lambda p: p.ticker):
                custo = CalculosCarteira.valor_posicao(LOTE_COMPRA, posicao.cotacao)
                if custo > saldo:
                    continue
                alvo = patrimonio_planejado * posicao.objetivo_percentual / 100
                desvio = alvo - valores[posicao.ticker]
                melhoria = desvio * desvio - (desvio - custo) * (desvio - custo)
                if melhoria > melhor_melhoria:
                    melhor_ticker, melhor_melhoria, melhor_custo = posicao.ticker, melhoria, custo
            if melhor_ticker is None:
                break
            sugestoes[melhor_ticker] += LOTE_COMPRA
            valores[melhor_ticker] += melhor_custo
            saldo -= melhor_custo

        investido = aporte - saldo
        patrimonio_projetado = patrimonio_atual + investido
        ativos = []
        for posicao in posicoes:
            atual = CalculosCarteira.valor_posicao(posicao.quantidade, posicao.cotacao)
            participacao_atual = CalculosCarteira.participacao(atual, patrimonio_atual)
            projetada = CalculosCarteira.participacao(valores[posicao.ticker], patrimonio_projetado)
            quantidade_sugerida = sugestoes[posicao.ticker]
            ativos.append(ProjecaoAtivo(
                ticker=posicao.ticker,
                objetivo_percentual=posicao.objetivo_percentual,
                quantidade_atual=posicao.quantidade,
                participacao_atual=participacao_atual,
                distancia_atual=posicao.objetivo_percentual - participacao_atual,
                quantidade_sugerida=quantidade_sugerida,
                custo_sugerido=CalculosCarteira.valor_posicao(quantidade_sugerida, posicao.cotacao),
                quantidade_projetada=posicao.quantidade + quantidade_sugerida,
                valor_projetado=valores[posicao.ticker],
                participacao_projetada=projetada,
                distancia_projetada=posicao.objetivo_percentual - projetada,
            ))
        return SimulacaoRebalanceamento(
            patrimonio_atual=patrimonio_atual,
            aporte=aporte,
            valor_investido=investido,
            saldo_restante=saldo,
            patrimonio_projetado=patrimonio_projetado,
            ativos=ativos,
        )
