"""Exercita o fluxo HTTP real da US 13 com persistencia, sem simular respostas da API."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.modules.assets.models import AtivoCarteira
from app.modules.quotes.models import Cotacao
from app.modules.transactions.models import Transacao
from app.modules.assets.repository import AtivoCarteiraRepository, AtivoRepository
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.service import CarteiraService
from app.modules.quotes.repository import CotacaoRepository
from app.modules.quotes.service import CotacaoService
from app.modules.transactions.repository import TransacaoRepository
from app.modules.transactions.service import TransacaoService, ErroTransacao
from app.modules.transactions.schemas import TransacaoEntrada


@pytest.mark.parametrize("aporte,saldo", [("3000", "0.00"), ("3500", "500.00"), ("600", "600.00")])
def test_sync_regras_e_persistencia(banco, faculdade, aporte, saldo):
    """Verifica camadas reais com banco isolado, inclusive quando sockets estao bloqueados."""
    ativos = AtivoRepository(banco)
    carteiras = CarteiraRepository(banco)
    cotacoes = CotacaoService(CotacaoRepository(banco), ativos)
    service = CarteiraService(carteiras)
    id_investidor = faculdade.id_investidor
    resultado = service.simular_aporte(faculdade.id_carteira, id_investidor, Decimal(aporte),
        AtivoCarteiraRepository(banco), ativos, cotacoes)
    assert resultado.saldo_restante == Decimal(saldo)
    compras = [a for a in resultado.ativos if a.quantidade_sugerida]
    assert [(a.ticker, a.quantidade_sugerida) for a in compras] == ([] if aporte == "600" else [("ABEV3", 200), ("CRFB3", 100)])
    assert banco.query(Transacao).count() == 0
    if not compras:
        return
    transacoes = TransacaoService(TransacaoRepository(banco), carteiras, ativos)
    entradas = [TransacaoEntrada(id_carteira=faculdade.id_carteira, ticker=a.ticker, tipo="compra",
        quantidade=a.quantidade_sugerida, preco_unitario=a.cotacao) for a in compras]
    transacoes.registrar_compras_recomendadas(entradas, id_investidor)
    assert len(transacoes.listar_transacoes(id_investidor, faculdade.id_carteira)) == 2
    resumo = service.calcular_resumo(faculdade.id_carteira, id_investidor, AtivoCarteiraRepository(banco), cotacoes)
    assert resumo.patrimonio_total == Decimal("13000.00")
    assert {a.ticker: a.participacao_percentual for a in resumo.ativos} == {
        "ABEV3": Decimal("30.77"), "CRFB3": Decimal("23.08"), "BBDC3": Decimal("15.38"),
        "EGIE3": Decimal("15.38"), "ITUB4": Decimal("15.38")}


def test_sync_rollback_e_linear(banco, faculdade):
    """Confere rollback real apos primeiro flush e distribuicao linear em carteira balanceada."""
    ativos = AtivoRepository(banco)
    carteiras = CarteiraRepository(banco)
    service = TransacaoService(TransacaoRepository(banco), carteiras, ativos)
    entradas = [TransacaoEntrada(id_carteira=faculdade.id_carteira, ticker=t, tipo="compra", quantidade=100, preco_unitario="10.00") for t in ("ABEV3", "ZZZZ3")]
    with pytest.raises(ErroTransacao):
        service.registrar_compras_recomendadas(entradas, faculdade.id_investidor)
    banco.expire_all()
    assert banco.query(Transacao).count() == 0
    assert banco.query(AtivoCarteira).filter_by(id_carteira=faculdade.id_carteira, ticker="ABEV3").one().quantidade == 200
    from app.modules.portfolios.calculos import CalculosCarteira, PosicaoParaRebalanceamento
    posicoes = [PosicaoParaRebalanceamento("A", 700, Decimal(10), Decimal(70)), PosicaoParaRebalanceamento("B", 300, Decimal(10), Decimal(30))]
    balanceamento = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal(10000))
    assert balanceamento.valor_investido == 0
    linear = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal(10000), "linear")
    assert [a.quantidade_sugerida for a in linear.ativos] == [700, 300]


def test_sync_total_pago_exato_sem_recalcular_pela_media(banco, faculdade):
    """Preserva R$ 532,00 por 300 acoes, cuja media nao tem duas casas exatas."""
    service = TransacaoService(TransacaoRepository(banco), CarteiraRepository(banco), AtivoRepository(banco))
    entrada = TransacaoEntrada(id_carteira=faculdade.id_carteira, ticker="ABEV3", tipo="compra",
        quantidade=300, preco_unitario="1.75", valor_total_pago="532.00")
    service.registrar_compras_recomendadas([entrada], faculdade.id_investidor)
    banco.expire_all()
    historico = service.listar_transacoes(faculdade.id_investidor, faculdade.id_carteira)
    assert len(historico) == 1
    assert historico[0].valor_total == Decimal("532.00")
    assert historico[0].preco_unitario == Decimal("1.77")  # Media informativa arredondada.
    assert historico[0].valor_total != historico[0].preco_unitario * 300
    assert banco.query(AtivoCarteira).filter_by(id_carteira=faculdade.id_carteira, ticker="ABEV3").one().quantidade == 500


@pytest.mark.parametrize("total", ["0", "-1", "532.001", "NaN", "Infinity"])
def test_sync_total_pago_invalido(total):
    """Rejeita valores que nao podem representar um pagamento real em centavos."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        TransacaoEntrada(id_carteira=1, ticker="ABEV3", tipo="compra", quantidade=300,
            preco_unitario="1.75", valor_total_pago=total)


@pytest.fixture
def faculdade(banco, criar_investidor, criar_carteira):
    """Monta exatamente o patrimonio e as metas do exemplo de aceite."""
    investidor = criar_investidor()
    carteira = criar_carteira(investidor.id_investidor, "Faculdade", [
        ("ABEV3", 40, 200), ("BBDC3", 10, 100), ("CRFB3", 30, 200),
        ("EGIE3", 10, 100), ("ITUB4", 10, 200),
    ])
    for ticker, preco in [("ABEV3", 10), ("BBDC3", 20), ("CRFB3", 10), ("EGIE3", 20), ("ITUB4", 10)]:
        banco.add(Cotacao(ticker=ticker, preco=Decimal(preco), data_atualizacao=datetime.now(timezone.utc).replace(tzinfo=None)))
    banco.commit()
    return carteira


@pytest.mark.parametrize("aporte,saldo", [("3000", "0.00"), ("3500", "500.00")])
async def test_simulacao_registro_historico_e_participacao(cliente, banco, faculdade, login, aporte, saldo):
    """Consulta sugestao, confirma compras e confere historico e patrimonio pela API."""
    headers = await login("marina.souza", "Marina@2025")
    caminho = f"/portfolios/{faculdade.id_carteira}"
    resposta = await cliente.post(caminho + "/contribution-simulation", headers=headers, json={"aporte": aporte})
    assert resposta.status_code == 200, resposta.text
    simulacao = resposta.json()
    compras = [a for a in simulacao["ativos"] if a["quantidade_sugerida"]]
    assert [(a["ticker"], a["quantidade_sugerida"], a["custo_sugerido"]) for a in compras] == [
        ("ABEV3", 200, "2000.00"), ("CRFB3", 100, "1000.00")]
    assert simulacao["saldo_restante"] == saldo
    assert banco.query(Transacao).count() == 0
    registro = await cliente.post("/transactions/recommended-purchases", headers=headers, json={"compras": [
        {"id_carteira": faculdade.id_carteira, "ticker": a["ticker"], "tipo": "compra",
         "quantidade": a["quantidade_sugerida"], "preco_unitario": a["cotacao"]} for a in compras]})
    assert registro.status_code == 201, registro.text
    historico = await cliente.get("/transactions", params={"id_carteira": faculdade.id_carteira}, headers=headers)
    assert len(historico.json()) == 2
    resumo = (await cliente.get(caminho + "/summary", headers=headers)).json()
    assert resumo["patrimonio_total"] == "13000.00"
    por_ticker = {a["ticker"]: a for a in resumo["ativos"]}
    assert por_ticker["ABEV3"]["quantidade"] == 400
    assert por_ticker["CRFB3"]["quantidade"] == 300
    assert por_ticker["ABEV3"]["participacao_percentual"] == "30.77"
    assert por_ticker["CRFB3"]["participacao_percentual"] == "23.08"


async def test_falha_no_segundo_item_desfaz_primeiro(cliente, banco, faculdade, login):
    """Uma compra valida seguida de ativo inexistente nao deixa gravacao parcial."""
    headers = await login("marina.souza", "Marina@2025")
    resposta = await cliente.post("/transactions/recommended-purchases", headers=headers, json={"compras": [
        {"id_carteira": faculdade.id_carteira, "ticker": t, "tipo": "compra", "quantidade": 100, "preco_unitario": "10.00"}
        for t in ("ABEV3", "ZZZZ3")]})
    assert resposta.status_code == 404
    banco.expire_all()
    assert banco.query(Transacao).count() == 0
    assert banco.query(AtivoCarteira).filter_by(id_carteira=faculdade.id_carteira, ticker="ABEV3").one().quantidade == 200


async def test_aporte_insuficiente_e_distribuicao_linear(cliente, faculdade, login):
    """A simulacao mantem saldo e oferece distribuicao proporcional as metas."""
    headers = await login("marina.souza", "Marina@2025")
    caminho = f"/portfolios/{faculdade.id_carteira}/contribution-simulation"
    baixo = (await cliente.post(caminho, headers=headers, json={"aporte": "600"})).json()
    assert all(a["quantidade_sugerida"] == 0 for a in baixo["ativos"])
    assert baixo["saldo_restante"] == "600.00"
    linear = (await cliente.post(caminho, headers=headers, json={"aporte": "10000", "distribuicao": "linear"})).json()
    assert {a["ticker"]: a["quantidade_sugerida"] for a in linear["ativos"]} == {
        "ABEV3": 400, "BBDC3": 0, "CRFB3": 300, "EGIE3": 0, "ITUB4": 100}
