"""Ponto de entrada da API FastAPI."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import ProjectException
from app.modules.assets.router import router as assets_router
from app.modules.auth.router import router as auth_router
from app.modules.investors.router import router as investors_router
from app.modules.portfolios.router import router as portfolios_router
from app.modules.transactions.router import router as transactions_router

# Garante que os modelos sejam registrados no metadata do SQLAlchemy.
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.investors import models as investors_models  # noqa: F401
from app.modules.portfolios import models as portfolios_models  # noqa: F401
from app.modules.assets import models as assets_models  # noqa: F401
from app.modules.transactions import models as transactions_models  # noqa: F401


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(investors_router)
app.include_router(portfolios_router)
app.include_router(assets_router)
app.include_router(transactions_router)


@app.exception_handler(ProjectException)
async def project_exception_handler(
    _request: Request,
    exc: ProjectException,
) -> JSONResponse:
    """Converte erros de negocio em respostas HTTP previsiveis."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Verifica se a API esta disponivel."""
    return {"status": "ok", "app": settings.app_name}
