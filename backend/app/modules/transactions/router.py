"""Rotas HTTP do modulo de transacoes."""

from fastapi import APIRouter


router = APIRouter(prefix="/transactions", tags=["transactions"])
