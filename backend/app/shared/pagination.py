"""Utilitarios compartilhados para paginacao."""


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def normalize_page_size(page_size: int) -> int:
    """Garante que o tamanho da pagina fique dentro do limite permitido."""
    return min(max(page_size, 1), MAX_PAGE_SIZE)
