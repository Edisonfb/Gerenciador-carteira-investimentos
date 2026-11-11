"""US 1.1 - Login do investidor."""

from app.core.security import hash_senha
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService

MENSAGEM_INVALIDO = "E-mail, nome de usuário ou senha inválidos"


# ---------- unitarios (service) ----------

def test_service_login_valido_retorna_token(banco, criar_investidor):
    criar_investidor()
    resultado = AuthService(AuthRepository(banco)).realizar_login(None, "marina.souza", "Marina@2025")
    assert resultado["token_type"] == "bearer"
    assert resultado["access_token"]


def test_service_login_ignora_maiusculas_e_espacos_no_usuario(banco, criar_investidor):
    criar_investidor()
    resultado = AuthService(AuthRepository(banco)).realizar_login(None, "  Marina.Souza ", "Marina@2025")
    assert resultado is not None


def test_service_login_senha_errada_retorna_none(banco, criar_investidor):
    criar_investidor()
    assert AuthService(AuthRepository(banco)).realizar_login(None, "marina.souza", "SenhaErrada1") is None


def test_service_login_conta_inativa_retorna_false(banco, criar_investidor):
    criar_investidor(ativo=False)
    assert AuthService(AuthRepository(banco)).realizar_login(None, "marina.souza", "Marina@2025") is False


def test_senha_salva_com_hash_e_nao_em_texto(banco, criar_investidor):
    investidor = criar_investidor()
    assert investidor.senha_hash != "Marina@2025"
    assert investidor.senha_hash != hash_senha("Marina@2025")  # o hash usa salt


# ---------- API (httpx + pytest-asyncio) ----------

async def test_cenario1_login_com_credenciais_validas(cliente, criar_investidor):
    criar_investidor()
    resposta = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert resposta.status_code == 200
    token = resposta.json()["access_token"]

    eu = await cliente.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert eu.status_code == 200
    assert eu.json()["tipo_usuario"] == "investidor"
    assert eu.json()["nome_usuario"] == "marina.souza"


async def test_cenario2_login_com_senha_incorreta(cliente, criar_investidor):
    criar_investidor()
    resposta = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "SenhaErrada1"})
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == MENSAGEM_INVALIDO
    assert "access_token" not in resposta.json()


async def test_cenario3_conta_inativa_nao_entra(cliente, criar_investidor):
    criar_investidor(ativo=False)
    resposta = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza", "senha": "Marina@2025"})
    assert resposta.status_code == 403
    assert "inativo" in resposta.json()["detail"].lower()


async def test_cenario4_investidor_nao_acessa_gerar_token(cliente, investidor_logado):
    resposta = await cliente.post("/investors", json={"email": "novo@example.test"}, headers=investidor_logado)
    assert resposta.status_code == 403


async def test_cenario5_campos_obrigatorios_em_branco(cliente, criar_investidor):
    criar_investidor()
    sem_usuario = await cliente.post("/auth/login", json={"nome_usuario": "", "senha": "Marina@2025"})
    sem_senha = await cliente.post("/auth/login", json={"nome_usuario": "marina.souza"})
    assert sem_usuario.status_code == 422
    assert sem_senha.status_code == 422


async def test_cenario6_usuario_nao_cadastrado(cliente, criar_investidor):
    criar_investidor()
    resposta = await cliente.post("/auth/login", json={"nome_usuario": "usuario_inexistente", "senha": "Marina@2025"})
    assert resposta.status_code == 401
    # Mesma mensagem da senha errada: nao indica qual dos dois esta incorreto.
    assert resposta.json()["detail"] == MENSAGEM_INVALIDO


async def test_rota_protegida_sem_token_retorna_401(cliente):
    resposta = await cliente.get("/auth/me")
    assert resposta.status_code == 401
