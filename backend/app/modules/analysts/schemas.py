from pydantic import BaseModel

class CadastroAnalistaEntrada(BaseModel):
    nome: str
    email: str
    senha: str

class AnalistaSaida(BaseModel):
    id_analista: int
    id_usuario: int
    nome: str
    email: str