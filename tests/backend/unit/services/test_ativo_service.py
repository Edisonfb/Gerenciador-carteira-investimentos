"""Valida as regras do catálogo de ativos sem acessar o banco."""

from unittest.mock import Mock

import pytest

from app.modules.assets.models import Ativo
from app.modules.assets.repository import AtivoRepository
from app.modules.assets.schemas import AtivoAtualizacaoEntrada, AtivoCadastroEntrada
from app.modules.assets.service import AtivoService


@pytest.fixture
def repository():
    """Fornece um repositório simulado com retorno dos objetos atualizados."""
    repository = Mock(spec=AtivoRepository)
    repository.buscar_por_codigo.return_value = None
    repository.atualizar.side_effect = lambda ativo: ativo
    return repository


def test_cadastro_normaliza_codigo_e_setor(repository):
    """Remove espaços e padroniza o código antes da persistência."""
    service = AtivoService(repository)
    resultado, erro = service.criar_ativo(
        AtivoCadastroEntrada(codigo=" petr4 ", setor=" Petróleo ")
    )

    assert erro is None
    assert resultado is repository.adicionar.return_value
    ativo = repository.adicionar.call_args.args[0]
    assert ativo.codigo == "PETR4"
    assert ativo.setor == "Petróleo"


@pytest.mark.parametrize(
    "codigo,setor",
    [("", "Energia"), ("   ", "Energia"), ("A" * 11, "Energia"),
     ("PETR4", ""), ("PETR4", "   "), ("PETR4", "A" * 81)],
)
def test_cadastro_rejeita_campos_invalidos(repository, codigo, setor):
    """Impede campos vazios e valores maiores que as colunas do banco."""
    resultado, erro = AtivoService(repository).criar_ativo(
        AtivoCadastroEntrada(codigo=codigo, setor=setor)
    )

    assert resultado is None
    assert erro
    repository.adicionar.assert_not_called()


def test_cadastro_rejeita_codigo_duplicado(repository):
    """Impede cadastrar outro ativo com um código existente."""
    repository.buscar_por_codigo.return_value = Ativo(id_ativo=1, codigo="PETR4")
    resultado, erro = AtivoService(repository).criar_ativo(
        AtivoCadastroEntrada(codigo="PETR4", setor="Petróleo")
    )

    assert resultado is None
    assert erro == "Já existe um ativo com esse código"
    repository.adicionar.assert_not_called()


@pytest.mark.parametrize(
    "campos,esperado",
    [({"codigo": " vale3 "}, ("VALE3", "Petróleo", True)),
     ({"setor": " Energia "}, ("PETR4", "Energia", True)),
     ({"ativo": False}, ("PETR4", "Petróleo", False))],
)
def test_atualizacao_parcial_preserva_campos_omitidos(repository, campos, esperado):
    """Atualiza um campo por vez, inclusive a desativação com False."""
    ativo = Ativo(id_ativo=1, codigo="PETR4", setor="Petróleo", ativo=True)
    repository.buscar_por_id.return_value = ativo

    resultado, erro = AtivoService(repository).atualizar_ativo(
        1, AtivoAtualizacaoEntrada(**campos)
    )

    assert resultado is ativo
    assert erro is None
    assert (ativo.codigo, ativo.setor, ativo.ativo) == esperado


@pytest.mark.parametrize("campo", ["codigo", "setor", "ativo"])
def test_atualizacao_rejeita_null_explicito(repository, campo):
    """Distingue campos omitidos de campos enviados explicitamente como null."""
    repository.buscar_por_id.return_value = Ativo(id_ativo=1, codigo="PETR4")
    resultado, erro = AtivoService(repository).atualizar_ativo(
        1, AtivoAtualizacaoEntrada(**{campo: None})
    )

    assert resultado is None
    assert erro
    repository.atualizar.assert_not_called()


def test_atualizacao_aceita_manter_o_proprio_codigo(repository):
    """Permite manter o código quando o resultado da busca é o próprio ativo."""
    ativo = Ativo(id_ativo=1, codigo="PETR4", setor="Petróleo")
    repository.buscar_por_id.return_value = ativo
    repository.buscar_por_codigo.return_value = ativo

    resultado, erro = AtivoService(repository).atualizar_ativo(
        1, AtivoAtualizacaoEntrada(codigo="PETR4")
    )

    assert resultado is ativo
    assert erro is None


def test_atualizacao_rejeita_codigo_de_outro_ativo(repository):
    """Informa o conflito de código e preserva os dados originais."""
    ativo = Ativo(id_ativo=1, codigo="PETR4", setor="Petróleo")
    repository.buscar_por_id.return_value = ativo
    repository.buscar_por_codigo.return_value = Ativo(id_ativo=2, codigo="VALE3")

    resultado, erro = AtivoService(repository).atualizar_ativo(
        1, AtivoAtualizacaoEntrada(codigo="VALE3")
    )

    assert resultado is None
    assert erro == "Já existe um ativo com esse código."
    assert ativo.codigo == "PETR4"
    repository.atualizar.assert_not_called()


def test_atualizacao_invalida_nao_altera_o_objeto(repository):
    """Valida todos os campos antes de modificar o objeto persistido."""
    ativo = Ativo(id_ativo=1, codigo="PETR4", setor="Petróleo")
    repository.buscar_por_id.return_value = ativo

    resultado, erro = AtivoService(repository).atualizar_ativo(
        1, AtivoAtualizacaoEntrada(codigo="VALE3", setor="   ")
    )

    assert resultado is None
    assert erro
    assert (ativo.codigo, ativo.setor) == ("PETR4", "Petróleo")
    repository.atualizar.assert_not_called()


def test_atualizacao_de_id_inexistente(repository):
    """Retorna erro de ativo inexistente sem tentar persistir alterações."""
    repository.buscar_por_id.return_value = None
    resultado, erro = AtivoService(repository).atualizar_ativo(
        99, AtivoAtualizacaoEntrada(setor="Energia")
    )

    assert resultado is None
    assert erro == "Ativo não encontrado"
    repository.atualizar.assert_not_called()


@pytest.mark.parametrize("existe", [True, False])
def test_exclusao_interna_verifica_existencia(repository, existe):
    """Exclui somente objetos encontrados, sem expor operação HTTP de escrita."""
    ativo = Ativo(id_ativo=1, codigo="PETR4") if existe else None
    repository.buscar_por_id.return_value = ativo

    assert AtivoService(repository).excluir_ativo(1) is existe
    if existe:
        repository.excluir.assert_called_once_with(ativo)
    else:
        repository.excluir.assert_not_called()
