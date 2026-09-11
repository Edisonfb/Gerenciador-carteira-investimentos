"""Testes unitarios da paginacao compartilhada."""

from app.shared.pagination import MAX_PAGE_SIZE, normalize_page_size


def test_normalize_page_size_respeita_limites() -> None:
    assert normalize_page_size(0) == 1
    assert normalize_page_size(20) == 20
    assert normalize_page_size(MAX_PAGE_SIZE + 50) == MAX_PAGE_SIZE
