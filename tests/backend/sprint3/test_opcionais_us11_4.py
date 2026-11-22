"""US 11.4 cenario 3 (opcional) - Falha ao atualizar a carteira."""

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.modules.assets.models import AtivoCarteira
from app.modules.investors.models import Investidor
from app.modules.transactions.models import Transacao


async def test_us11_4_cenario3_falha_ao_atualizar_a_carteira(banco, investidor_logado, criar_carteira, transacao, monkeypatch):
    carteira = criar_carteira(banco.query(Investidor).first().id_investidor, "Aposentadoria", [("ITUB4", 100, 100)])

    def falha_ao_gravar(self):
        raise StaleDataError("a linha do ativo mudou durante a gravação")

    with monkeypatch.context() as falso:
        falso.setattr(Session, "commit", falha_ao_gravar)
        resposta = await transacao(investidor_logado, carteira.id_carteira, "ITUB4", "compra", 200)

    # A tela traduz o 409 para "Não foi possível concluir a transação. Tente novamente".
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Conflito ao registrar a transação. Tente novamente."
    banco.expire_all()
    assert banco.query(Transacao).count() == 0
    assert banco.query(AtivoCarteira).filter_by(id_carteira=carteira.id_carteira, ticker="ITUB4").one().quantidade == 100
