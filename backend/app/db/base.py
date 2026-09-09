"""Base declarativa usada pelos modelos do SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base para todos os modelos persistidos no banco."""
