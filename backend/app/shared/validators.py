"""Validadores compartilhados entre os modulos da aplicacao."""

import csv
import re
from pathlib import Path


ARQUIVO_ATIVOS_B3 = Path(__file__).resolve().parent / "dados" / "ativos_b3.csv"

# Codigo do ativo: quatro letras e um numero, sem espacos ou caracteres
# especiais (ex.: PETR4, ITUB3). Os quatro primeiros caracteres identificam
# a empresa; aceita numeros neles por causa de B3SA3 e G2DI3.
PADRAO_CODIGO_ATIVO = re.compile(r"^([A-Z0-9]{4})\d$")


def _carregar_codigos_b3() -> frozenset[str]:
    """Le os codigos das empresas da lista setorial da B3 usada no projeto."""
    with open(ARQUIVO_ATIVOS_B3, encoding="utf-8") as arquivo:
        return frozenset(linha["codigo"] for linha in csv.DictReader(arquivo))


CODIGOS_ATIVOS_B3 = _carregar_codigos_b3()


def is_positive_number(value: float) -> bool:
    """Verifica se um numero e maior que zero."""
    return value > 0


def validar_codigo_ativo(codigo: str | None) -> bool:
    """Verifica se o codigo do ativo e valido e a empresa esta listada na B3."""
    if not codigo:
        return False

    resultado = PADRAO_CODIGO_ATIVO.match(codigo.upper())
    if resultado is None:
        return False

    codigo_empresa = resultado.group(1)
    return codigo_empresa in CODIGOS_ATIVOS_B3
