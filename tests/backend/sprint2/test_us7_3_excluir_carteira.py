"""US 7.3 - Exclusao de carteira."""

from app.modules.assets.models import AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.portfolios.repository import CarteiraRepository
from app.modules.portfolios.service import CarteiraService


def test_service_excluir_carteira_de_outro_investidor_retorna_false(banco, criar_investidor, criar_carteira):
    dono = criar_investidor()
    carteira = criar_carteira(dono.id_investidor, "Carro")
    assert CarteiraService(CarteiraRepository(banco)).excluir_carteira(carteira.id_carteira, id_investidor=999) is False


async def test_cenario1_exclusao_remove_so_a_carteira_escolhida(cliente, banco, investidor_logado, criar_carteira):
    investidor = banco.query(Investidor).first()
    aposentadoria = criar_carteira(investidor.id_investidor, "Aposentadoria", [("ABEV3", 50), ("ITUB4", 50)])
    carro = criar_carteira(investidor.id_investidor, "Carro", [("AALR3", 100)])
    id_carro = carro.id_carteira

    resposta = await cliente.delete(f"/portfolios/{id_carro}", headers=investidor_logado)
    assert resposta.status_code == 204

    nomes = [c["nome"] for c in (await cliente.get("/portfolios", headers=investidor_logado)).json()]
    assert nomes == ["Aposentadoria"]
    # O conjunto de ativos do Carro sai junto; o da Aposentadoria fica.
    assert banco.query(AtivoCarteira).filter_by(id_carteira=id_carro).count() == 0
    ativos = (await cliente.get(f"/assets/carteira/{aposentadoria.id_carteira}", headers=investidor_logado)).json()
    assert [a["ticker"] for a in ativos] == ["ABEV3", "ITUB4"]


async def test_excluir_carteira_inexistente(cliente, investidor_logado):
    resposta = await cliente.delete("/portfolios/999", headers=investidor_logado)
    assert resposta.status_code == 404
