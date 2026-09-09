"""Rotas HTTP do modulo de autenticacao."""

from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])
