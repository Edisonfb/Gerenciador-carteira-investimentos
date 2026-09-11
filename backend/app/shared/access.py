"""Regras compartilhadas de acesso a investidores e recursos vinculados."""

from app.modules.auth.models import User
from app.modules.investors.models import Investor
from app.shared.roles import is_analyst, is_client


def user_can_access_investor(user: User, investor: Investor) -> bool:
    """Verifica se o usuario pode acessar o investidor (analista dono ou cliente vinculado)."""
    if is_analyst(user.role):
        return investor.user_id == user.id
    if is_client(user.role):
        return investor.account_user_id == user.id
    return False
