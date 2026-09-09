"""Rotas HTTP do modulo de carteiras."""

from fastapi import APIRouter


router = APIRouter(prefix="/portfolios", tags=["portfolios"])
