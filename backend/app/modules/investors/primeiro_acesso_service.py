"""Conclusao do cadastro por autorizacao temporaria, sem sessao de login."""
import hmac

import jwt

from app.core.config import settings
from app.db.enums import Tipo_Usuario
from app.modules.auth.password_service import assinatura_senha
from app.modules.investors.repository import InvestidorRepository
from app.modules.investors.schemas import CadastroPrimeiroAcessoEntrada, PrimeiroAcessoInvestidorEntrada
from app.modules.investors.service import InvestidorService


def concluir_cadastro_com_token(repository: InvestidorRepository, dados: CadastroPrimeiroAcessoEntrada):
    try:
        payload = jwt.decode(dados.token_definicao, settings.secret_key, algorithms=["HS256"],
                             options={"require": ["sub", "exp", "purpose", "fingerprint"]})
        if payload["purpose"] != "investor_setup":
            raise ValueError()
        investidor = repository.buscar_por_usuario_id_para_atualizacao(int(payload["sub"]))
        if (investidor is None or not investidor.ativo
            or investidor.tipo_usuario != Tipo_Usuario.INVESTIDOR
            or investidor.primeiro_acesso_concluido
            or not hmac.compare_digest(str(payload["fingerprint"]), assinatura_senha(investidor))):
            raise ValueError()
    except (jwt.InvalidTokenError, ValueError, TypeError) as erro:
        raise ValueError("Autorização inválida ou expirada. Valide novamente seu e-mail e token de convite.") from erro
    entrada = PrimeiroAcessoInvestidorEntrada(**dados.model_dump(exclude={"token_definicao"}))
    resultado, erro = InvestidorService(repository).concluir_primeiro_acesso(investidor.id_usuario, entrada)
    if erro is not None or resultado is None:
        raise ValueError(erro or "Não foi possível concluir o cadastro.")
    return resultado
