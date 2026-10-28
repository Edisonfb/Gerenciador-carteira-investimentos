"""Task: Validacao de codigo do ativo (shared/validators.py)."""

import pytest

from app.shared.validators import CODIGOS_ATIVOS_B3, validar_codigo_ativo


@pytest.mark.parametrize(
    "codigo",
    ["PETR4", "ITUB3", "VALE3", "BBAS3", "B3SA3", "G2DI3"],
)
def test_aceita_codigos_validos_listados_na_b3(codigo):
    assert validar_codigo_ativo(codigo) is True


def test_aceita_codigo_em_minusculas():
    assert validar_codigo_ativo("petr4") is True


@pytest.mark.parametrize("codigo", [None, ""])
def test_rejeita_codigo_vazio(codigo):
    assert validar_codigo_ativo(codigo) is False


@pytest.mark.parametrize(
    "codigo",
    [
        "PETR",     # sem numero
        "PET4",     # empresa com tres caracteres
        "PETRO4",   # empresa com cinco caracteres
        "PETR44",   # dois numeros no final
        "PETRA",    # termina com letra
        "PETR 4",   # espaco no meio
        " PETR4",   # espaco no inicio
        "PETR4 ",   # espaco no final
        "PE-R4",    # caractere especial
        "PETR4!",   # caractere especial no final
        "PÉTR4",    # acento
    ],
)
def test_rejeita_codigo_com_formato_invalido(codigo):
    assert validar_codigo_ativo(codigo) is False


@pytest.mark.parametrize("codigo", ["ZZZZ3", "ABCD4", "XPTO11"])
def test_rejeita_empresa_fora_da_lista_da_b3(codigo):
    assert validar_codigo_ativo(codigo) is False


def test_lista_da_b3_foi_carregada_do_csv():
    assert len(CODIGOS_ATIVOS_B3) > 400
    assert {"PETR", "ITUB", "B3SA", "G2DI"} <= CODIGOS_ATIVOS_B3
