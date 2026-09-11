"""Helpers reutilizaveis pelos testes."""


def make_investor_payload(**overrides):
    """Monta payload valido de pre-cadastro de cliente."""
    payload = {
        "first_name": "Maria",
        "last_name": "Silva",
        "rg": "1234567",
        "document": "12345678901",
        "email": "cliente@example.com",
        "phone": "51999999999",
        "address": "Rua Exemplo, 100 - Feliz/RS",
    }
    payload.update(overrides)
    return payload
