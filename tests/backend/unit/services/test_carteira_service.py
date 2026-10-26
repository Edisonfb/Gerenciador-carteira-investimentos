"""Task: Gerenciamento de carteira de investimento (CarteiraService)."""

import pytest

from app.modules.portfolios.models import Carteira
from app.modules.portfolios.schemas import (
    CarteiraAtualizacaoEntrada,
    CarteiraCadastroEntrada,
)
from app.modules.portfolios.service import CarteiraService


BUG_DESCRICAO = (
    "Bug: o modelo Carteira nao tem a coluna 'descricao', mas o service "
    "passa descricao= ao criar a carteira (TypeError)."
)


class RepositorioCarteiraFalso:
    def __init__(self):
        self.carteiras = []
        self.excluidas = []

    def adicionar(self, carteira):
        carteira.id_carteira = len(self.carteiras) + 1
        self.carteiras.append(carteira)
        return carteira

    def listar_por_investidor(self, id_investidor):
        return [c for c in self.carteiras if c.id_investidor == id_investidor]

    def buscar_por_id_e_investidor(self, id_carteira, id_investidor):
        return next(
            (
                c
                for c in self.carteiras
                if c.id_carteira == id_carteira and c.id_investidor == id_investidor
            ),
            None,
        )

    def atualizar(self, carteira):
        return carteira

    def excluir(self, carteira):
        self.carteiras.remove(carteira)
        self.excluidas.append(carteira)


@pytest.fixture
def repositorio():
    return RepositorioCarteiraFalso()


@pytest.fixture
def service(repositorio):
    return CarteiraService(repositorio)


def _carteira_existente(repositorio, id_investidor=1, nome="Aposentadoria"):
    carteira = Carteira(id_investidor=id_investidor, nome=nome, ativa=True)
    return repositorio.adicionar(carteira)


# Criacao


@pytest.mark.xfail(reason=BUG_DESCRICAO, raises=TypeError, strict=True)
def test_cria_carteira_com_nome_sem_espacos_extras(service):
    carteira, erro = service.criar_carteira(
        CarteiraCadastroEntrada(nome="  Aposentadoria  ", descricao="Longo prazo"),
        id_investidor=1,
    )

    assert erro is None
    assert carteira.nome == "Aposentadoria"
    assert carteira.id_investidor == 1


@pytest.mark.parametrize("nome", ["", "   "])
def test_criacao_exige_nome(service, repositorio, nome):
    carteira, erro = service.criar_carteira(CarteiraCadastroEntrada(nome=nome), id_investidor=1)

    assert carteira is None
    assert erro == "O nome da carteira é obrigatório."
    assert repositorio.carteiras == []


# Consulta


def test_lista_apenas_carteiras_do_investidor(service, repositorio):
    minha = _carteira_existente(repositorio, id_investidor=1)
    _carteira_existente(repositorio, id_investidor=2)

    assert service.listar_carteiras(1) == [minha]


def test_busca_carteira_do_proprio_investidor(service, repositorio):
    carteira = _carteira_existente(repositorio, id_investidor=1)

    assert service.buscar_carteira(carteira.id_carteira, 1) is carteira


def test_nao_busca_carteira_de_outro_investidor(service, repositorio):
    carteira = _carteira_existente(repositorio, id_investidor=2)

    assert service.buscar_carteira(carteira.id_carteira, 1) is None


# Atualizacao


def test_atualiza_somente_campos_enviados(service, repositorio):
    carteira = _carteira_existente(repositorio, nome="Antigo")

    atualizada, erro = service.atualizar_carteira(
        carteira.id_carteira, 1, CarteiraAtualizacaoEntrada(nome="  Novo  ", ativa=False)
    )

    assert erro is None
    assert atualizada.nome == "Novo"
    assert atualizada.ativa is False


def test_atualiza_descricao(service, repositorio):
    carteira = _carteira_existente(repositorio)

    atualizada, erro = service.atualizar_carteira(
        carteira.id_carteira, 1, CarteiraAtualizacaoEntrada(descricao="Reserva")
    )

    assert erro is None
    assert atualizada.descricao == "Reserva"
    assert atualizada.nome == "Aposentadoria"


def test_atualizacao_de_carteira_inexistente(service):
    carteira, erro = service.atualizar_carteira(99, 1, CarteiraAtualizacaoEntrada(nome="X"))

    assert carteira is None
    assert erro == "Carteira não encontrada"


def test_atualizacao_nao_alcanca_carteira_de_outro_investidor(service, repositorio):
    carteira = _carteira_existente(repositorio, id_investidor=2, nome="Dele")

    resultado, erro = service.atualizar_carteira(
        carteira.id_carteira, 1, CarteiraAtualizacaoEntrada(nome="Invadida")
    )

    assert resultado is None
    assert erro == "Carteira não encontrada"
    assert carteira.nome == "Dele"


@pytest.mark.parametrize(
    "dados, mensagem",
    [
        ({"nome": None}, "O nome da carteira é obrigatório."),
        ({"nome": "   "}, "O nome da carteira é obrigatório."),
        ({"ativa": None}, "O status da carteira é obrigatório."),
    ],
)
def test_atualizacao_valida_campos_obrigatorios(service, repositorio, dados, mensagem):
    carteira = _carteira_existente(repositorio, nome="Original")

    resultado, erro = service.atualizar_carteira(
        carteira.id_carteira, 1, CarteiraAtualizacaoEntrada(**dados)
    )

    assert resultado is None
    assert erro == mensagem
    assert carteira.nome == "Original"
    assert carteira.ativa is True


# Exclusao


def test_exclui_carteira_do_proprio_investidor(service, repositorio):
    carteira = _carteira_existente(repositorio)

    assert service.excluir_carteira(carteira.id_carteira, 1) is True
    assert repositorio.excluidas == [carteira]


def test_nao_exclui_carteira_inexistente_ou_de_outro_investidor(service, repositorio):
    carteira = _carteira_existente(repositorio, id_investidor=2)

    assert service.excluir_carteira(99, 1) is False
    assert service.excluir_carteira(carteira.id_carteira, 1) is False
    assert repositorio.excluidas == []
