"""Verifica a sugestão de aporte pela API sem alterar posições ou transações."""
from datetime import datetime, timezone
from decimal import Decimal

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.portfolios.models import Carteira
from app.modules.quotes.models import Cotacao
from app.modules.transactions.models import Transacao


def preparar_carteira(sessao_banco, investidor, *, metas=("50.00", "50.00")):
    """Cria duas ações com cotação conhecida e uma posição inicial."""
    carteira = Carteira(id_investidor=investidor.id_investidor, nome="Teste", ativa=True)
    sessao_banco.add(carteira)
    sessao_banco.flush()
    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    for ticker, quantidade, meta in zip(("AAAA3", "BBBB4"), (100, 0), metas):
        sessao_banco.add(Ativo(ticker=ticker, nome=ticker, setor="Teste", ativo=True))
        sessao_banco.add(AtivoCarteira(
            ticker=ticker, id_carteira=carteira.id_carteira,
            quantidade=quantidade, objetivo_percentual=Decimal(meta),
        ))
        sessao_banco.add(Cotacao(
            ticker=ticker, preco=Decimal("10.00"), data_atualizacao=agora,
        ))
    sessao_banco.commit()
    return carteira


async def test_sugere_lote_e_preserva_carteira(cliente, sessao_banco, criar_investidor, login):
    """Expõe valor atual e compras sugeridas sem executar uma compra."""
    investidor = criar_investidor()
    carteira = preparar_carteira(sessao_banco, investidor)
    cabecalho = await login("investidor@teste.com")

    resposta = await cliente.post(
        f"/portfolios/{carteira.id_carteira}/contribution-simulation",
        json={"aporte": "1000.00"}, headers=cabecalho,
    )

    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["patrimonio_atual"] == "1000.00"
    assert dados["valor_investido"] == "1000.00"
    assert dados["saldo_restante"] == "0.00"
    assert dados["patrimonio_projetado"] == "2000.00"
    assert [(ativo["ticker"], ativo["quantidade_sugerida"]) for ativo in dados["ativos"]] == [
        ("AAAA3", 0), ("BBBB4", 100),
    ]
    assert dados["ativos"][0]["valor_atual"] == "1000.00"
    assert dados["ativos"][1]["cotacao"] == "10.00"
    assert dados["ativos"][1]["custo_sugerido"] == "1000.00"
    assert dados["ativos"][1]["participacao_projetada"] == "50.00"
    assert dados["ativos"][1]["data_atualizacao"]
    sessao_banco.expire_all()
    assert [v.quantidade for v in sessao_banco.query(AtivoCarteira).order_by(AtivoCarteira.ticker)] == [100, 0]
    assert sessao_banco.query(Transacao).count() == 0


async def test_sugestao_rejeita_carteira_alheia_e_meta_incompleta(
    cliente, sessao_banco, criar_investidor, login,
):
    """Protege a carteira e sinaliza objetivos que não formam 100%."""
    investidor = criar_investidor()
    carteira = preparar_carteira(sessao_banco, investidor, metas=("40.00", "40.00"))
    outro = criar_investidor(email="outro@teste.com")
    cabecalho_outro = await login("outro@teste.com")
    resposta_alheia = await cliente.post(
        f"/portfolios/{carteira.id_carteira}/contribution-simulation",
        json={"aporte": "1000.00"}, headers=cabecalho_outro,
    )
    assert resposta_alheia.status_code == 404
    assert outro.id_investidor != investidor.id_investidor

    cabecalho = await login("investidor@teste.com")
    resposta_metas = await cliente.post(
        f"/portfolios/{carteira.id_carteira}/contribution-simulation",
        json={"aporte": "1000.00"}, headers=cabecalho,
    )
    assert resposta_metas.status_code == 400
    assert "100%" in resposta_metas.json()["detail"]


async def test_sugestao_exige_aporte_valido(cliente, sessao_banco, criar_investidor, login):
    """Recusa valores sem centavos válidos e campos adicionais."""
    investidor = criar_investidor()
    carteira = preparar_carteira(sessao_banco, investidor)
    cabecalho = await login("investidor@teste.com")
    caminho = f"/portfolios/{carteira.id_carteira}/contribution-simulation"

    for corpo in ({"aporte": "0"}, {"aporte": "10.001"}, {"aporte": "100", "ticker": "AAAA3"}):
        resposta = await cliente.post(caminho, json=corpo, headers=cabecalho)
        assert resposta.status_code == 422
