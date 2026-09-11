"""Constantes e helpers de perfil de usuario."""

ROLE_ANALYST = "analyst"
ROLE_CLIENT = "client"
VALID_ROLES = {ROLE_ANALYST, ROLE_CLIENT}


def is_analyst(role: str) -> bool:
    """Indica se o perfil e de analista."""
    return role == ROLE_ANALYST


def is_client(role: str) -> bool:
    """Indica se o perfil e de cliente."""
    return role == ROLE_CLIENT
