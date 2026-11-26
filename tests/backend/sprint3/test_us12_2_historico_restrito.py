"""US 12.2 - Historico restrito a carteira e ao investidor (SCRUM-63)."""

from sqlalchemy import text

from app.modules.investors.models import Investidor


async def historico(cliente, cabecalho, **filtros):
    resposta = await cliente.get("/transactions", headers=cabecalho, params=filtros)
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


async def test_cenario1_transacoes_de_outra_carteira_nao_aparecem(cliente, banco, investidor_logado, criar_carteira,
                                                                    cotacoes_17_11, transacao):
    id_marina = banco.query(Investidor).first().id_investidor
    aposentadoria = criar_carteira(id_marina, "Aposentadoria", [("ITUB4", 100, 0)])
    casa = criar_carteira(id_marina, "Casa", [("ITUB4", 100, 0)])
    carro = criar_carteira(id_marina, "Carro", [("ITUB4", 100, 0)])
    compra_aposentadoria = (await transacao(investidor_logado, aposentadoria.id_carteira, "ITUB4", "compra", 200)).json()
    await transacao(investidor_logado, carro.id_carteira, "ITUB4", "compra", 100, data_transacao="2026-11-17T20:00:00-03:00")

    lista = await historico(cliente, investidor_logado, id_carteira=aposentadoria.id_carteira)
    assert [t["id_transacao"] for t in lista] == [compra_aposentadoria["id_transacao"]]
    assert all(t["nome_carteira"] == "Aposentadoria" for t in lista)
    assert await historico(cliente, investidor_logado, id_carteira=casa.id_carteira) == []


async def test_cenario2_historico_de_outro_investidor(cliente, banco, criar_investidor, criar_carteira, login,
                                                      investidor_logado, cotacoes_17_11, transacao):
    carlos = criar_investidor(nome_usuario="carlos.lima", senha="Carlos@2025", email="carlos.lima@example.test",
                              email_recuperacao="carlos.lima2@example.test")
    viagem = criar_carteira(carlos.id_investidor, "Viagem", [("ITUB4", 100, 0)])
    cabecalho_carlos = await login("carlos.lima", "Carlos@2025")
    await transacao(cabecalho_carlos, viagem.id_carteira, "ITUB4", "compra", 100)

    # A tela do historico abre a carteira primeiro; para a marina ela nao existe.
    carteira = await cliente.get(f"/portfolios/{viagem.id_carteira}", headers=investidor_logado)
    assert carteira.status_code == 404
    # E nenhuma transacao do carlos e devolvida, mesmo pedindo a carteira dele.
    assert await historico(cliente, investidor_logado, id_carteira=viagem.id_carteira) == []
    assert await historico(cliente, investidor_logado) == []


# ---------- regras extras ----------

async def test_historico_continua_depois_de_excluir_a_carteira(cliente, banco, investidor_logado, criar_carteira,
                                                               cotacoes_17_11, transacao):
    banco.execute(text("PRAGMA foreign_keys=ON"))  # o SQLite so aplica ON DELETE SET NULL com isso ligado
    carro = criar_carteira(banco.query(Investidor).first().id_investidor, "Carro", [("ITUB4", 100, 0)])
    await transacao(investidor_logado, carro.id_carteira, "ITUB4", "compra", 100)
    # US 8.3 cenario 2.1: a carteira so pode ser excluida depois de vender as acoes.
    await transacao(investidor_logado, carro.id_carteira, "ITUB4", "venda", 100)
    assert (await cliente.delete(f"/portfolios/{carro.id_carteira}", headers=investidor_logado)).status_code == 204

    lista = await historico(cliente, investidor_logado)
    assert len(lista) == 2
    assert all(item["nome_carteira"] == "Carro" for item in lista)
    assert all(item["id_carteira"] is None for item in lista)
