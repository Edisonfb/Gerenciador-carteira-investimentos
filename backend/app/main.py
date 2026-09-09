"""Ponto de entrada da API FastAPI."""

from fastapi import FastAPI

from app.core.config import settings
from app.modules.assets.router import router as assets_router
from app.modules.auth.router import router as auth_router
from app.modules.investors.router import router as investors_router
from app.modules.portfolios.router import router as portfolios_router
from app.modules.transactions.router import router as transactions_router


app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(investors_router)
app.include_router(portfolios_router)
app.include_router(assets_router)
app.include_router(transactions_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Verifica se a API esta disponivel."""
    return {"status": "ok", "app": settings.app_name}
