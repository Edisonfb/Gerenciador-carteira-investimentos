"""Tasks 64, 32 e 63: registro de transacao, atualizacao da carteira e historico."""
from decimal import Decimal

import pytest

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.portfolios.models import Carteira
from app.modules.transactions.models import Transacao
from app.shared import yahoo_finance


@pytest.fixture(autouse=True)
def yahoo(monkeypatch):
    """Cotacao fixa de R$ 10,00 para todos os ativos."""
    monkeypatch.setattr(yahoo_finance, "buscar_preco", lambda ticker: Decimal("10.00"))


@pytest.fixture
async def investidor_logado(criar_investidor, login):
    investidor = criar_investidor()
    return investidor, await login("investidor@teste.com")


@pytest.fixture
def criar_carteira(sessao_banco):
    """Cria uma carteira com PETR4 e VALE3, ambos com quantidade inicial."""
    def _criar(investidor, nome="Aposentadoria", quantidade=0, ativa=True):
        for ticker in ("PETR4", "VALE3"):
            if sessao_banco.get(Ativo, ticker) is None:
                sessao_banco.add(Ativo(ticker=ticker, setor="Setor"))
        carteira = Carteira(id_investidor=investidor.id_investidor, nome=nome, ativa=ativa)
        sessao_banco.add(carteira)
        sessao_banco.flush()
        for ticker in ("PETR4", "VALE3"):
            sessao_banco.add(AtivoCarteira(
                ticker=ticker, id_carteira=carteira.id_carteira,
                quantidade=quantidade, objetivo_percentual=Decimal("50"),
            ))
        sessao_banco.commit()
        return carteira

    return _criar


def quantidade_na_carteira(sessao_banco, id_carteira, ticker="PETR4"):
    sessao_banco.expire_all()
    return sessao_banco.get(AtivoCarteira, (ticker, id_carteira)).quantidade


def transacao(id_carteira, tipo="compra", quantidade=100, ticker="PETR4"):
    return {"id_carteira": id_carteira, "ticker": ticker, "tipo": tipo, "quantidade": quantidade}


# Registro (Task 64) e atualizacao da carteira (Task 32)


async def test_compra_registra_transacao_e_soma_quantidade(cliente, investidor_logado, criar_carteira, sessao_banco):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira, quantidade=200), headers=cabecalho)

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["tipo"] == "compra"
    assert dados["nome_carteira"] == "Aposentadoria"
    assert Decimal(dados["preco_unitario"]) == Decimal("10.00")
    assert Decimal(dados["valor_total"]) == Decimal("2000.00")
    assert quantidade_na_carteira(sessao_banco, carteira.id_carteira) == 200


async def test_venda_subtrai_quantidade(cliente, investidor_logado, criar_carteira, sessao_banco):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor, quantidade=300)

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira, "venda", 100), headers=cabecalho)

    assert resposta.status_code == 201
    assert quantidade_na_carteira(sessao_banco, carteira.id_carteira) == 200


async def test_venda_maior_que_a_quantidade_e_recusada(cliente, investidor_logado, criar_carteira, sessao_banco):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor, quantidade=100)

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira, "venda", 200), headers=cabecalho)

    assert resposta.status_code == 400
    assert "Quantidade insuficiente" in resposta.json()["detail"]
    assert quantidade_na_carteira(sessao_banco, carteira.id_carteira) == 100
    assert sessao_banco.query(Transacao).count() == 0


@pytest.mark.parametrize("quantidade", [1, 99, 150])
async def test_quantidade_fora_do_lote_de_100_e_recusada(cliente, investidor_logado, criar_carteira, quantidade):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira, quantidade=quantidade), headers=cabecalho)

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A quantidade deve ser em lotes de 100 ações."


@pytest.mark.parametrize("corpo", [
    {"tipo": "deposito"},
    {"quantidade": 0},
    {"quantidade": -100},
    {"quantidade": "100"},
    {"preco_unitario": 5},
])
async def test_corpo_fora_do_contrato_retorna_422(cliente, investidor_logado, criar_carteira, corpo):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)

    resposta = await cliente.post("/transactions", json={**transacao(carteira.id_carteira), **corpo}, headers=cabecalho)

    assert resposta.status_code == 422


async def test_nao_registra_em_carteira_de_outro_investidor(cliente, criar_investidor, criar_carteira, login):
    dono = criar_investidor("dono@teste.com")
    criar_investidor("outro@teste.com")
    carteira = criar_carteira(dono)
    cabecalho = await login("outro@teste.com")

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira), headers=cabecalho)

    assert resposta.status_code == 404


async def test_ativo_que_nao_esta_na_carteira_retorna_404(cliente, investidor_logado, criar_carteira, sessao_banco):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)
    sessao_banco.add(Ativo(ticker="ITUB4", setor="Financeiro"))
    sessao_banco.commit()

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira, ticker="ITUB4"), headers=cabecalho)

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Ativo não encontrado nesta carteira."


async def test_carteira_desativada_nao_recebe_transacao(cliente, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor, ativa=False)

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira), headers=cabecalho)

    assert resposta.status_code == 400


async def test_sem_cotacao_nao_registra_transacao(cliente, investidor_logado, criar_carteira, sessao_banco, monkeypatch):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)

    def yahoo_fora_do_ar(ticker):
        raise RuntimeError("Yahoo fora do ar")
    monkeypatch.setattr(yahoo_finance, "buscar_preco", yahoo_fora_do_ar)

    resposta = await cliente.post("/transactions", json=transacao(carteira.id_carteira), headers=cabecalho)

    assert resposta.status_code == 503
    assert quantidade_na_carteira(sessao_banco, carteira.id_carteira) == 0
    assert sessao_banco.query(Transacao).count() == 0


async def test_analista_nao_registra_transacao(cliente, criar_analista, login):
    criar_analista()
    cabecalho = await login("analista@teste.com")

    resposta = await cliente.post("/transactions", json=transacao(1), headers=cabecalho)

    assert resposta.status_code == 403


# Historico (Task 63)


async def test_historico_lista_apenas_transacoes_do_investidor(cliente, criar_investidor, criar_carteira, login):
    investidor = criar_investidor("investidor@teste.com")
    outro = criar_investidor("outro@teste.com")
    minha = criar_carteira(investidor)
    alheia = criar_carteira(outro, nome="Outra")
    cabecalho = await login("investidor@teste.com")
    cabecalho_outro = await login("outro@teste.com")
    await cliente.post("/transactions", json=transacao(minha.id_carteira), headers=cabecalho)
    await cliente.post("/transactions", json=transacao(alheia.id_carteira), headers=cabecalho_outro)

    resposta = await cliente.get("/transactions", headers=cabecalho)

    assert resposta.status_code == 200
    assert [t["id_carteira"] for t in resposta.json()] == [minha.id_carteira]


async def test_historico_mostra_mais_recentes_primeiro(cliente, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)
    await cliente.post("/transactions", json=transacao(carteira.id_carteira, "compra", 300), headers=cabecalho)
    await cliente.post("/transactions", json=transacao(carteira.id_carteira, "venda", 100), headers=cabecalho)

    resposta = await cliente.get("/transactions", headers=cabecalho)

    assert [t["tipo"] for t in resposta.json()] == ["venda", "compra"]


async def test_historico_filtra_por_carteira_ticker_e_tipo(cliente, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    aposentadoria = criar_carteira(investidor)
    carro = criar_carteira(investidor, nome="Carro")
    await cliente.post("/transactions", json=transacao(aposentadoria.id_carteira, "compra", 200), headers=cabecalho)
    await cliente.post("/transactions", json=transacao(aposentadoria.id_carteira, "venda", 100), headers=cabecalho)
    await cliente.post("/transactions", json=transacao(aposentadoria.id_carteira, ticker="VALE3"), headers=cabecalho)
    await cliente.post("/transactions", json=transacao(carro.id_carteira), headers=cabecalho)

    por_carteira = await cliente.get("/transactions", params={"id_carteira": carro.id_carteira}, headers=cabecalho)
    por_ticker = await cliente.get("/transactions", params={"ticker": "vale3"}, headers=cabecalho)
    por_tipo = await cliente.get("/transactions", params={"tipo": "venda"}, headers=cabecalho)

    assert [t["nome_carteira"] for t in por_carteira.json()] == ["Carro"]
    assert [t["ticker"] for t in por_ticker.json()] == ["VALE3"]
    assert [t["tipo"] for t in por_tipo.json()] == ["venda"]


async def test_historico_permanece_depois_de_excluir_a_carteira(cliente, investidor_logado, criar_carteira):
    investidor, cabecalho = investidor_logado
    carteira = criar_carteira(investidor)
    await cliente.post("/transactions", json=transacao(carteira.id_carteira, "compra", 100), headers=cabecalho)
    await cliente.post("/transactions", json=transacao(carteira.id_carteira, "venda", 100), headers=cabecalho)

    exclusao = await cliente.delete(f"/portfolios/{carteira.id_carteira}", headers=cabecalho)
    resposta = await cliente.get("/transactions", headers=cabecalho)

    assert exclusao.status_code == 204
    assert len(resposta.json()) == 2
    assert all(t["nome_carteira"] == "Aposentadoria" for t in resposta.json())


async def test_historico_exige_token(cliente):
    resposta = await cliente.get("/transactions")

    assert resposta.status_code == 401
