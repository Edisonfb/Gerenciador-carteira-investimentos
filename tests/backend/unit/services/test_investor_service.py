"""Testes unitarios do servico de investidores."""

from types import SimpleNamespace

from app.modules.investors.schemas import PrimeiroAcessoInvestidorEntrada
from app.modules.investors.service import InvestidorService


class InvestidorRepositoryFake:
    """Simula as consultas usadas no primeiro acesso do investidor."""

    def __init__(self, investidor, usuario_com_nome=None):
        self.investidor = investidor
        self.usuario_com_nome = usuario_com_nome

    def buscar_por_usuario_id(self, id_usuario):
        return self.investidor if id_usuario == self.investidor.id_usuario else None

    def buscar_usuario_por_nome_usuario(self, nome_usuario):
        return self.usuario_com_nome

    def buscar_usuario_por_email(self, email):
        return None

    def buscar_por_email_recuperacao(self, email_recuperacao):
        return None

    def atualizar(self, investidor):
        return investidor


def test_concluir_primeiro_acesso_define_nome_usuario_do_investidor(monkeypatch):
    investidor = SimpleNamespace(
        id_usuario=1,
        email="investidor@email.com",
        nome_usuario=None,
        email_recuperacao=None,
        senha_hash="token-inicial",
        primeiro_acesso_concluido=False,
    )
    dados = PrimeiroAcessoInvestidorEntrada(
        nome_usuario=" InvestidorUm ",
        email_recuperacao="recuperacao@email.com",
        nova_senha="senha-definitiva",
    )
    service = InvestidorService(InvestidorRepositoryFake(investidor))
    monkeypatch.setattr("app.modules.investors.service.hash_senha", lambda senha: f"hash-{senha}")

    resultado, erro = service.concluir_primeiro_acesso(1, dados)

    assert erro is None
    assert resultado.nome_usuario == "investidorum"
    assert resultado.email_recuperacao == "recuperacao@email.com"
    assert resultado.senha_hash == "hash-senha-definitiva"
    assert resultado.primeiro_acesso_concluido is True


def test_concluir_primeiro_acesso_rejeita_nome_usuario_repetido():
    investidor = SimpleNamespace(
        id_usuario=1,
        email="investidor@email.com",
        nome_usuario=None,
        primeiro_acesso_concluido=False,
    )
    usuario_com_nome = SimpleNamespace(id_usuario=2)
    dados = PrimeiroAcessoInvestidorEntrada(
        nome_usuario="investidor",
        email_recuperacao="recuperacao@email.com",
        nova_senha="senha-definitiva",
    )
    service = InvestidorService(InvestidorRepositoryFake(investidor, usuario_com_nome))

    resultado, erro = service.concluir_primeiro_acesso(1, dados)

    assert resultado is None
    assert erro == "Já existe um usuário com este nome de usuário."
