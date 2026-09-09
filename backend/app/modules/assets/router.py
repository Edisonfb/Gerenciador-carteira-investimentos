"""Rotas HTTP do modulo de ativos financeiros."""

from fastapi import APIRouter


router = APIRouter(prefix="/assets", tags=["assets"])
