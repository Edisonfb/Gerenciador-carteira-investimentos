"""Rotas HTTP do modulo de investidores."""

from fastapi import APIRouter


router = APIRouter(prefix="/investors", tags=["investors"])
