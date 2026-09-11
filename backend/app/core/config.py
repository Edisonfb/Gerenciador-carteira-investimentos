"""Configuracoes gerais lidas a partir de variaveis de ambiente."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


class Settings:
    """Centraliza configuracoes usadas pelo backend."""

    app_name: str = os.getenv(
        "APP_NAME",
        "Gerenciador de Carteiras de Investimento",
    )
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://portfolio_user:portfolio_password@localhost:3306/"
        "investment_portfolio_manager",
    )
    secret_key: str = os.getenv(
        "SECRET_KEY",
        "change-me-in-production-use-a-long-random-string",
    )
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
