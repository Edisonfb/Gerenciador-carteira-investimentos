"""Utilitarios para normalizar e gerar nomes de usuario."""


def normalizar_nome_usuario(nome_usuario: str) -> str:
    """Padroniza o nome de usuario antes de salvar ou consultar."""
    return nome_usuario.strip().lower()
