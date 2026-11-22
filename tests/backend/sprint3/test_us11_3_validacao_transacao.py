"""US 11.3 - Validacao dos dados da transacao (SCRUM-64).

As mensagens da historia sao exibidas pela tela Transacao; aqui se confere que a
API recusa os mesmos dados e que nada e gravado.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.transactions.models import Transacao


@pytest.fixture
async def aposentadoria(banco, investidor_logado, criar_carteira, cotacoes_17_11):
    investidor = banco.query(Investidor).first()
    return criar_carteira(investidor.id_investidor, "Aposentadoria", [
        ("ABEV3", 50, 100), ("BBDC4", 20, 100), ("EGIE3", 20, 100), ("ITUB4", 10, 100),
    ])


def nada_gravado(banco, id_carteira):
    banco.expire_all()
    itub4 = banco.query(AtivoCarteira).filter_by(id_carteira=id_carteira, ticker="ITUB4").one()
    return banco.query(Transacao).count() == 0 and itub4.quantidade == 100


async def enviar(cliente, cabecalho, corpo):
    return await cliente.post("/transactions", headers=cabecalho, json=corpo)


def corpo_compra(carteira, **alteracoes):
    corpo = {"id_carteira": carteira, "ticker": "ITUB4", "tipo": "compra", "quantidade": 100, "preco_unitario": "40.89"}
    corpo.update(alteracoes)
    return {campo: valor for campo, valor in corpo.items() if valor is not None}


async def test_cenario1_quantidade_nao_informada(cliente, banco, investidor_logado, aposentadoria):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, quantidade=None))
    assert resposta.status_code == 422
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_cenario2_quantidade_que_nao_e_multipla_de_100(cliente, banco, investidor_logado, aposentadoria):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, quantidade=150))
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A quantidade deve ser em lotes de 100 ações."
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_cenario3_quantidade_abaixo_do_lote_minimo(cliente, banco, investidor_logado, aposentadoria):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, quantidade=50))
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A quantidade deve ser em lotes de 100 ações."
    assert nada_gravado(banco, aposentadoria.id_carteira)


@pytest.mark.parametrize("valor", [0, -100, "abc"])
async def test_cenario4_quantidade_zero_negativa_ou_nao_numerica(cliente, banco, investidor_logado, aposentadoria, valor):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, quantidade=valor))
    assert resposta.status_code == 422
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_cenario5_ativo_que_nao_pertence_a_carteira(cliente, banco, investidor_logado, aposentadoria):
    banco.add(Ativo(ticker="PETR4", setor="Energia"))
    banco.commit()
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, ticker="PETR4"))
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Ativo não encontrado nesta carteira."
    assert nada_gravado(banco, aposentadoria.id_carteira)


@pytest.mark.parametrize("campo", ["id_carteira", "ticker"])
async def test_cenario6_carteira_ou_ativo_nao_selecionado(cliente, banco, investidor_logado, aposentadoria, campo):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, **{campo: None}))
    assert resposta.status_code == 422
    assert nada_gravado(banco, aposentadoria.id_carteira)


@pytest.mark.parametrize("tipo", [None, "deposito"])
async def test_cenario7_tipo_da_transacao_nao_escolhido(cliente, banco, investidor_logado, aposentadoria, tipo):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, tipo=tipo))
    assert resposta.status_code == 422
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_cenario8_analista_nao_registra_transacoes(cliente, banco, aposentadoria, login):
    # O analista paulo.ramos foi criado junto com a investidora, como responsavel por ela.
    cabecalho = await login("paulo.ramos", "1234")
    resposta = await enviar(cliente, cabecalho, corpo_compra(aposentadoria.id_carteira))
    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Esta operação é permitida apenas para investidores."
    historico = await cliente.get("/transactions", headers=cabecalho)
    assert historico.status_code == 403
    assert nada_gravado(banco, aposentadoria.id_carteira)


# ---------- regras extras ----------

async def test_carteira_inexistente(cliente, investidor_logado, aposentadoria):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(999))
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Carteira não encontrada."


async def test_carteira_de_outro_investidor(cliente, banco, aposentadoria, criar_investidor, login):
    criar_investidor(nome_usuario="carlos.lima", senha="Carlos@2025", email="carlos.lima@example.test",
                     email_recuperacao="carlos.lima2@example.test")
    cabecalho_carlos = await login("carlos.lima", "Carlos@2025")
    resposta = await enviar(cliente, cabecalho_carlos, corpo_compra(aposentadoria.id_carteira))
    assert resposta.status_code == 404
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_ativo_fora_do_catalogo(cliente, investidor_logado, aposentadoria):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, ticker="ZZZZ9"))
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Ativo não encontrado."


@pytest.mark.parametrize("preco", ["0", "-10.00", "40.891", "abc"])
async def test_preco_invalido(cliente, banco, investidor_logado, aposentadoria, preco):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, preco_unitario=preco))
    assert resposta.status_code == 422
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_campo_fora_do_contrato(cliente, banco, investidor_logado, aposentadoria):
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, setor="Financeiro"))
    assert resposta.status_code == 422
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_data_no_futuro(cliente, banco, investidor_logado, aposentadoria):
    amanha = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    resposta = await enviar(cliente, investidor_logado, corpo_compra(aposentadoria.id_carteira, data_transacao=amanha))
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "A data da transação não pode ser futura."
    assert nada_gravado(banco, aposentadoria.id_carteira)


async def test_sem_login(cliente, banco, aposentadoria):
    resposta = await enviar(cliente, {}, corpo_compra(aposentadoria.id_carteira))
    assert resposta.status_code == 401
    assert nada_gravado(banco, aposentadoria.id_carteira)
