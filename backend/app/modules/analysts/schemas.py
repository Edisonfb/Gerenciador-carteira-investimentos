from pydantic import BaseModel, ConfigDict

class CadastroAnalistaEntrada(BaseModel):
    nome: str
    email: str
    nome_usuario: str
    senha: str

class AnalistaSaida(BaseModel):
    id_analista: int
    id_usuario: int
    nome: str
    email: str
    nome_usuario: str | None

class AnalistaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str | None = None
    email: str | None = None
