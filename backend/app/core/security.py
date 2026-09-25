"""Funcoes de seguranca do backend.

Este arquivo deve concentrar recursos como autenticacao, autorizacao,
hash de senhas e validacao de tokens quando essas funcionalidades forem
implementadas.
"""
import hmac

def verificar_senha(senha_digitada: str, senha_salva: str) -> bool:
    return hmac.compare_digest(senha_digitada, senha_salva)