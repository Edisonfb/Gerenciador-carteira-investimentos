"""Item 1 - Autenticacao no Sistema (Investidor): convite e primeiro acesso.

O analista cadastra o investidor so com o e-mail; o investidor recebe um
token inicial por e-mail e, no primeiro acesso, troca esse token por uma
senha definitiva e informa um e-mail de recuperacao.
"""

import pytest

from app.core.security import hash_senha, verificar_senha
from app.db.enums import Tipo_Usuario
from app.modules.investors import service as investidor_service_modulo
from app.modules.investors.models import Investidor
from app.modules.investors.schemas import (
    CadastroInvestidorEntrada,
    PrimeiroAcessoInvestidorEntrada,
)
from app.modules.investors.service import InvestidorService


class RepositorioInvestidorFalso:
    def __init__(self):
        self.investidores = []
        self.outros_emails = set()
        self.confirmado = False
        self.desfeito = False

    def buscar_usuario_por_email(self, email):
        if email in self.outros_emails:
            return object()
        return next((i for i in self.investidores if i.email == email), None)

    def buscar_por_email_recuperacao(self, email_recuperacao):
        return next(
            (i for i in self.investidores if i.email_recuperacao == email_recuperacao),
            None,
        )

    def buscar_por_usuario_id(self, id_usuario):
        return next((i for i in self.investidores if i.id_usuario == id_usuario), None)

    def adicionar(self, investidor):
        investidor.id_usuario = len(self.investidores) + 1
        self.investidores.append(investidor)
        return investidor

    def confirmar(self):
        self.confirmado = True

    def desfazer(self):
        self.desfeito = True

    def atualizar(self, investidor):
        return investidor


@pytest.fixture
def repositorio():
    return RepositorioInvestidorFalso()


@pytest.fixture
def emails_enviados(monkeypatch):
    enviados = []
    monkeypatch.setattr(
        investidor_service_modulo.email_service,
        "enviar_token_acesso",
        lambda email, token: enviados.append((email, token)),
    )
    return enviados


def _investidor_convidado(repositorio, email="investidor@teste.com", token="token-inicial"):
    investidor = Investidor(
        id_usuario=10,
        email=email,
        senha_hash=hash_senha(token),
        tipo_usuario=Tipo_Usuario.INVESTIDOR,
        id_analista_responsavel=1,
        primeiro_acesso_concluido=False,
    )
    repositorio.investidores.append(investidor)
    return investidor


def _primeiro_acesso(email_recuperacao="recuperacao@teste.com", nova_senha="NovaSenha123"):
    return PrimeiroAcessoInvestidorEntrada(
        email_recuperacao=email_recuperacao, nova_senha=nova_senha
    )


# Cadastro (convite) do investidor


def test_cadastro_envia_token_inicial_e_guarda_apenas_o_hash(repositorio, emails_enviados):
    service = InvestidorService(repositorio)

    investidor, erro = service.cadastrar_investidor(
        CadastroInvestidorEntrada(email="  Investidor@Teste.com "), id_analista_responsavel=5
    )

    assert erro is None
    assert investidor.email == "investidor@teste.com"
    assert investidor.id_analista_responsavel == 5
    assert investidor.primeiro_acesso_concluido is False
    assert repositorio.confirmado is True

    [(email_destino, token)] = emails_enviados
    assert email_destino == "investidor@teste.com"
    assert investidor.senha_hash != token
    assert verificar_senha(token, investidor.senha_hash) is True


def test_cadastro_rejeita_email_vazio(repositorio, emails_enviados):
    investidor, erro = InvestidorService(repositorio).cadastrar_investidor(
        CadastroInvestidorEntrada(email="   "), id_analista_responsavel=1
    )

    assert investidor is None
    assert erro == "O e-mail do investidor é obrigatório."
    assert emails_enviados == []


def test_cadastro_rejeita_email_ja_usado(repositorio, emails_enviados):
    repositorio.outros_emails.add("existente@teste.com")

    investidor, erro = InvestidorService(repositorio).cadastrar_investidor(
        CadastroInvestidorEntrada(email="existente@teste.com"), id_analista_responsavel=1
    )

    assert investidor is None
    assert erro == "Já existe um usuário com este e-mail."
    assert emails_enviados == []


def test_cadastro_desfaz_quando_envio_de_email_falha(repositorio, monkeypatch):
    def falhar(email, token):
        raise RuntimeError("SMTP fora do ar")

    monkeypatch.setattr(investidor_service_modulo.email_service, "enviar_token_acesso", falhar)

    with pytest.raises(RuntimeError):
        InvestidorService(repositorio).cadastrar_investidor(
            CadastroInvestidorEntrada(email="novo@teste.com"), id_analista_responsavel=1
        )

    assert repositorio.desfeito is True
    assert repositorio.confirmado is False


# Primeiro acesso


def test_primeiro_acesso_troca_token_por_senha_definitiva(repositorio):
    _investidor_convidado(repositorio, token="token-inicial")

    investidor, erro = InvestidorService(repositorio).concluir_primeiro_acesso(
        10, _primeiro_acesso(email_recuperacao=" Recuperacao@Teste.com ")
    )

    assert erro is None
    assert investidor.primeiro_acesso_concluido is True
    assert investidor.email_recuperacao == "recuperacao@teste.com"
    assert verificar_senha("NovaSenha123", investidor.senha_hash) is True
    assert verificar_senha("token-inicial", investidor.senha_hash) is False


def test_primeiro_acesso_sem_perfil_de_investidor(repositorio):
    investidor, erro = InvestidorService(repositorio).concluir_primeiro_acesso(99, _primeiro_acesso())

    assert investidor is None
    assert erro == "Perfil de investidor não encontrado."


def test_primeiro_acesso_nao_pode_ser_repetido(repositorio):
    _investidor_convidado(repositorio).primeiro_acesso_concluido = True

    investidor, erro = InvestidorService(repositorio).concluir_primeiro_acesso(10, _primeiro_acesso())

    assert investidor is None
    assert erro == "O primeiro acesso deste investidor já foi concluído."


@pytest.mark.parametrize(
    "dados, mensagem",
    [
        (
            {"email_recuperacao": "  "},
            "O e-mail de recuperação é obrigatório.",
        ),
        (
            {"email_recuperacao": "INVESTIDOR@teste.com"},
            "O e-mail de recuperação deve ser diferente do e-mail principal.",
        ),
        (
            {"nova_senha": "   "},
            "A nova senha é obrigatória.",
        ),
    ],
)
def test_primeiro_acesso_valida_campos(repositorio, dados, mensagem):
    convidado = _investidor_convidado(repositorio)
    hash_original = convidado.senha_hash

    investidor, erro = InvestidorService(repositorio).concluir_primeiro_acesso(
        10, _primeiro_acesso(**dados)
    )

    assert investidor is None
    assert erro == mensagem
    assert convidado.primeiro_acesso_concluido is False
    assert convidado.senha_hash == hash_original


def test_primeiro_acesso_rejeita_email_de_recuperacao_que_e_email_principal_de_outro(repositorio):
    _investidor_convidado(repositorio)
    repositorio.outros_emails.add("analista@teste.com")

    investidor, erro = InvestidorService(repositorio).concluir_primeiro_acesso(
        10, _primeiro_acesso(email_recuperacao="analista@teste.com")
    )

    assert investidor is None
    assert erro == "O e-mail de recuperação já está cadastrado como e-mail principal."


def test_primeiro_acesso_rejeita_email_de_recuperacao_ja_usado(repositorio):
    _investidor_convidado(repositorio)
    outro = _investidor_convidado(repositorio, email="outro@teste.com")
    outro.id_usuario = 11
    outro.email_recuperacao = "recuperacao@teste.com"

    investidor, erro = InvestidorService(repositorio).concluir_primeiro_acesso(10, _primeiro_acesso())

    assert investidor is None
    assert erro == "Este e-mail de recuperação já está em uso."
