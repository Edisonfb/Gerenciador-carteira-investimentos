"""Valida o catalogo integrado e a autorizacao antes da persistencia."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.modules.assets.models import Ativo, AtivoCarteira
from app.modules.assets.repository import AtivoRepository, AtivoCarteiraRepository
from app.modules.assets.schemas import (
    CadastroAtivoEntrada, CadastroAtivoCarteiraEntrada,
    AtivoAtualizacaoEntrada, AtivoCarteiraUpdate,
)
from app.modules.assets.service import AtivoService, AtivoCarteiraService, ErroAtivo
from app.modules.portfolios.repository import CarteiraRepository


@pytest.fixture
def repository():
    """Fornece o repositorio sem acessar um banco real."""
    repo = Mock(spec=AtivoRepository)
    repo.buscar_por_codigo.return_value = None
    repo.salvar.side_effect = lambda ativo: ativo
    repo.atualizar.side_effect = lambda ativo: ativo
    return repo


def test_cadastro_normaliza_codigo_e_setor(repository):
    """Preserva normalizacao e aceita codigo como alias legado."""
    ativo, erro = AtivoService(repository).criar_ativo(
        CadastroAtivoEntrada(codigo=" petr4 ", setor=" Petróleo "),
    )
    assert erro is None
    assert ativo.ticker == ativo.codigo == "PETR4"
    assert ativo.setor == "Petróleo"


@pytest.mark.parametrize("ticker,setor", [
    ("", "Energia"), ("   ", "Energia"), ("A" * 11, "Energia"),
    ("PETR 4", "Energia"), ("PETR4", ""), ("PETR4", "   "),
    ("PETR4", "A" * 256),
])
def test_cadastro_rejeita_campos_invalidos(ticker, setor):
    """Campos invalidos sao rejeitados antes do servico."""
    with pytest.raises(ValidationError):
        CadastroAtivoEntrada(ticker=ticker, setor=setor)


def test_duplicidade_e_concorrencia_no_catalogo(repository):
    """Rejeita cadastro duplicado, inclusive quando a disputa ocorre no commit."""
    service = AtivoService(repository)
    dados = CadastroAtivoEntrada(ticker="PETR4", setor="Energia")
    repository.buscar_por_codigo.return_value = Ativo(ticker="PETR4")
    assert service.criar_ativo(dados)[1]
    repository.salvar.assert_not_called()
    repository.buscar_por_codigo.return_value = None
    repository.salvar.side_effect = IntegrityError("insert", {}, Exception())
    assert service.criar_ativo(dados)[1]


def test_atualizacao_preserva_campos_omitidos_e_rejeita_null(repository):
    """Nao aplica mudancas parciais se houver campo nulo explicito."""
    ativo = Ativo(ticker="PETR4", setor="Energia", ativo=True)
    repository.buscar_por_codigo.return_value = ativo
    service = AtivoService(repository)
    assert service.atualizar_ativo("PETR4", AtivoAtualizacaoEntrada(ativo=False)) == (ativo, None)
    assert ativo.ativo is False
    assert ativo.setor == "Energia"
    assert service.atualizar_ativo(
        "PETR4", AtivoAtualizacaoEntrada(setor=None, nome="Nao aplicar"),
    )[1]
    assert ativo.nome is None


@pytest.mark.parametrize("quantidade", [True, False, -1, 1.5, "2", None, 2147483648])
def test_quantidade_invalida_em_cadastro_e_atualizacao(quantidade):
    """Cadastro e atualizacao rejeitam quantidades invalidas."""
    with pytest.raises(ValidationError):
        CadastroAtivoCarteiraEntrada(ticker="PETR4", id_carteira=1, quantidade=quantidade, objetivo_percentual="20.00")
    if quantidade is None:
        # O schema permite omissao; null explicito e rejeitado pelo servico.
        assert AtivoCarteiraUpdate(quantidade=None).model_dump(exclude_unset=True) == {"quantidade": None}
    else:
        with pytest.raises(ValidationError):
            AtivoCarteiraUpdate(quantidade=quantidade)


def test_carteira_alheia_nao_consulta_nem_persiste_ativos():
    """A autorizacao deve acontecer antes de revelar dados do catalogo/vinculo."""
    vinculos = Mock(spec=AtivoCarteiraRepository)
    carteiras = Mock(spec=CarteiraRepository)
    ativos = Mock(spec=AtivoRepository)
    carteiras.buscar_por_id_e_investidor.return_value = None
    service = AtivoCarteiraService(vinculos, carteiras, ativos)
    with pytest.raises(ErroAtivo) as erro:
        service.cadastrar_ativo_carteira(
            CadastroAtivoCarteiraEntrada(ticker="PETR4", id_carteira=2, quantidade=1, objetivo_percentual="20.00"), 7,
        )
    assert erro.value.status_code == 404
    ativos.buscar_por_codigo.assert_not_called()
    vinculos.salvar.assert_not_called()


def test_conflito_concorrente_de_vinculo_e_traduzido():
    """Trata disputa no commit mesmo apos verificacao previa de duplicidade."""
    vinculos = Mock(spec=AtivoCarteiraRepository)
    carteiras = Mock(spec=CarteiraRepository)
    ativos = Mock(spec=AtivoRepository)
    carteiras.buscar_por_id_e_investidor.return_value = SimpleNamespace(ativa=True)
    ativos.buscar_por_codigo.return_value = SimpleNamespace(ativo=True)
    vinculos.buscar.return_value = None
    vinculos.salvar.side_effect = IntegrityError("insert", {}, Exception())
    service = AtivoCarteiraService(vinculos, carteiras, ativos)
    with pytest.raises(ErroAtivo) as erro:
        service.cadastrar_ativo_carteira(
            CadastroAtivoCarteiraEntrada(ticker="PETR4", id_carteira=2, quantidade=1, objetivo_percentual="20.00"), 7,
        )
    assert erro.value.status_code == 409


def test_exclusao_interna_preserva_ativos_com_posicoes(repository):
    """A manutencao do catalogo nao pode apagar uma posicao existente."""
    ativo = Ativo(ticker="PETR4", setor="Energia")
    ativo.ativos_carteira = [
        AtivoCarteira(
            ticker="PETR4", id_carteira=1, quantidade=2,
        )
    ]
    repository.buscar_por_codigo.return_value = ativo
    assert AtivoService(repository).excluir_ativo("PETR4") is False
    repository.excluir.assert_not_called()


@pytest.mark.parametrize("quantidade", [0, 1])
def test_cadastro_preserva_percentual_e_aceita_quantidade_zero(quantidade):
    from decimal import Decimal
    vinculos = Mock(spec=AtivoCarteiraRepository)
    carteiras = Mock(spec=CarteiraRepository)
    ativos = Mock(spec=AtivoRepository)
    carteiras.buscar_por_id_e_investidor.return_value = SimpleNamespace(ativa=True)
    ativos.buscar_por_codigo.return_value = SimpleNamespace(ativo=True)
    vinculos.buscar.return_value = None
    vinculos.salvar.side_effect = lambda vinculo: vinculo
    service = AtivoCarteiraService(vinculos, carteiras, ativos)
    resultado = service.cadastrar_ativo_carteira(CadastroAtivoCarteiraEntrada(
        ticker="ITUB4", id_carteira=1, quantidade=quantidade, objetivo_percentual="20.50",
    ), 7)
    assert resultado.quantidade == quantidade
    assert resultado.objetivo_percentual == Decimal("20.50")
    vinculos.excluir.assert_not_called()


def test_atualizar_para_zero_preserva_vinculo_e_objetivo():
    from decimal import Decimal
    vinculo = AtivoCarteira(ticker="ITUB4", id_carteira=1, quantidade=10, objetivo_percentual=Decimal("20.50"))
    vinculos = Mock(spec=AtivoCarteiraRepository)
    carteiras = Mock(spec=CarteiraRepository)
    ativos = Mock(spec=AtivoRepository)
    carteiras.buscar_por_id_e_investidor.return_value = SimpleNamespace(ativa=True)
    vinculos.buscar.return_value = vinculo
    vinculos.salvar.side_effect = lambda item: item
    service = AtivoCarteiraService(vinculos, carteiras, ativos)
    assert service.atualizar_quantidade(1, "ITUB4", AtivoCarteiraUpdate(quantidade=0), 7) is vinculo
    assert vinculo.quantidade == 0
    assert vinculo.objetivo_percentual == Decimal("20.50")
    vinculos.excluir.assert_not_called()
    vinculos.salvar.assert_called_once_with(vinculo)


def test_quantidade_zero_nao_permite_alterar_carteira_alheia():
    vinculos = Mock(spec=AtivoCarteiraRepository)
    carteiras = Mock(spec=CarteiraRepository)
    carteiras.buscar_por_id_e_investidor.return_value = None
    service = AtivoCarteiraService(vinculos, carteiras, Mock(spec=AtivoRepository))
    with pytest.raises(ErroAtivo) as erro:
        service.atualizar_quantidade(1, "ITUB4", AtivoCarteiraUpdate(quantidade=0), 7)
    assert erro.value.status_code == 404
    vinculos.buscar.assert_not_called()
    vinculos.salvar.assert_not_called()


@pytest.fixture
def contexto_atualizacao():
    from decimal import Decimal
    vinculo = AtivoCarteira(ticker="ITUB4", id_carteira=1, quantidade=10, objetivo_percentual=Decimal("20.50"))
    vinculos = Mock(spec=AtivoCarteiraRepository)
    carteiras = Mock(spec=CarteiraRepository)
    ativos = Mock(spec=AtivoRepository)
    carteiras.buscar_por_id_e_investidor.return_value = SimpleNamespace(ativa=True)
    ativos.buscar_por_codigo.return_value = SimpleNamespace(ativo=True)
    vinculos.buscar.return_value = vinculo
    vinculos.salvar.side_effect = lambda item: item
    return AtivoCarteiraService(vinculos, carteiras, ativos), vinculo


def test_atualiza_somente_percentual_sem_alterar_quantidade(contexto_atualizacao):
    from decimal import Decimal
    service, vinculo = contexto_atualizacao
    resultado = service.atualizar_quantidade(1, "ITUB4", AtivoCarteiraUpdate(objetivo_percentual="25.00"), 7)
    assert resultado is vinculo
    assert vinculo.quantidade == 10
    assert vinculo.objetivo_percentual == Decimal("25.00")
    service.repository.excluir.assert_not_called()


def test_atualiza_quantidade_e_percentual_juntos(contexto_atualizacao):
    from decimal import Decimal
    service, vinculo = contexto_atualizacao
    service.atualizar_quantidade(1, "ITUB4", AtivoCarteiraUpdate(quantidade=0, objetivo_percentual="30.25"), 7)
    assert vinculo.quantidade == 0
    assert vinculo.objetivo_percentual == Decimal("30.25")


@pytest.mark.parametrize("campos", [{}, {"quantidade": None}, {"objetivo_percentual": None}, {"quantidade": 5, "objetivo_percentual": None}])
def test_rejeita_campos_vazios_ou_nulos_sem_alterar_vinculo(contexto_atualizacao, campos):
    from decimal import Decimal
    service, vinculo = contexto_atualizacao
    with pytest.raises(ErroAtivo) as erro:
        service.atualizar_quantidade(1, "ITUB4", AtivoCarteiraUpdate(**campos), 7)
    assert erro.value.status_code == 400
    assert vinculo.quantidade == 10
    assert vinculo.objetivo_percentual == Decimal("20.50")
    service.repository.salvar.assert_not_called()


@pytest.mark.parametrize("alvo", ["carteira", "ativo"])
def test_percentual_nao_altera_recurso_desativado(contexto_atualizacao, alvo):
    service, vinculo = contexto_atualizacao
    if alvo == "carteira":
        service.carteiras.buscar_por_id_e_investidor.return_value.ativa = False
    else:
        service.ativos.buscar_por_codigo.return_value.ativo = False
    with pytest.raises(ErroAtivo) as erro:
        service.atualizar_quantidade(1, "ITUB4", AtivoCarteiraUpdate(objetivo_percentual="25"), 7)
    assert erro.value.status_code == 400
    assert vinculo.quantidade == 10
    service.repository.salvar.assert_not_called()
