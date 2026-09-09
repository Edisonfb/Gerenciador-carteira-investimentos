"""Configuracoes gerais lidas a partir de variaveis de ambiente."""

import os


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


settings = Settings()
