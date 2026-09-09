"""Validadores compartilhados entre os modulos da aplicacao."""


def is_positive_number(value: float) -> bool:
    """Verifica se um numero e maior que zero."""
    return value > 0
