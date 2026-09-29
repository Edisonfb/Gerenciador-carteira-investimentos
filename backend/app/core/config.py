import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(PROJECT_DIR / ".env")


def _build_database_url() -> str:
    """Monta a URL do banco a partir do .env quando DATABASE_URL nao existir."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    driver = os.getenv("DB_DRIVER", "mysql+pymysql")
    user = quote_plus(os.getenv("DB_USER", "portfolio_user"))
    password = quote_plus(os.getenv("DB_PASSWORD", "portfolio_password"))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME", "investment_portfolio_manager")

    return f"{driver}://{user}:{password}@{host}:{port}/{database}"


class Settings:
    """Centraliza configuracoes usadas pelo backend."""

    app_name: str = os.getenv(
        "APP_NAME",
        "Gerenciador de Carteiras de Investimento",
    )
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = _build_database_url()
    servidor_smtp: str = os.getenv("SMTP_HOST", "")
    porta_smtp: int = int(os.getenv("SMTP_PORT") or "587")
    usuario_smtp: str = os.getenv("SMTP_USER", "")
    senha_smtp: str = os.getenv("SMTP_PASSWORD", "")
    email_remetente: str = os.getenv("SMTP_FROM", "")
    usar_tls: bool = (os.getenv("SMTP_USE_TLS") or "true").lower() == "true"
    endereco_frontend: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    secret_key: str = os.getenv("SECRET_KEY", "development-only-change-this-secret")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )


settings = Settings()
