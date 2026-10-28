"""Schemas de entrada e saida do modulo de autenticacao."""

from pydantic import BaseModel, Field, ConfigDict, model_validator


class LoginEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    nome_usuario: str | None = None
    senha: str

    @model_validator(mode="after")
    def validar_identificacao(self):
        """Exige que o login use apenas e-mail ou nome de usuario."""
        tem_email = self.email is not None and bool(self.email.strip())
        tem_nome_usuario = self.nome_usuario is not None and bool(self.nome_usuario.strip())

        if tem_email == tem_nome_usuario:
            raise ValueError("Informe e-mail ou nome de usuário para fazer login.")

        return self


class UsuarioSaida(BaseModel):
    id_usuario: int
    email: str
    nome_usuario: str | None
    tipo_usuario: str
    ativo: bool


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutSaida(BaseModel):
    mensagem: str


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str | None = None
    nome_usuario: str | None = None
    ativo: bool | None = None


class SolicitarSenhaEntrada(BaseModel):
    email: str


class RedefinirSenhaEntrada(BaseModel):
    token: str
    senha: str


class PrimeiroAcessoEntrada(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    token: str = Field(min_length=1, max_length=255)


class PrimeiroAcessoSaida(BaseModel):
    token_definicao: str
