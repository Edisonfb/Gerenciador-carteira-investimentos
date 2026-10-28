"""Recursos de conexao e configuracao do banco de dados."""

from app.db.base import Base
from app.modules.auth.models import Usuario
from app.modules.analysts.models import Analista
from app.modules.investors.models import Investidor
from app.modules.portfolios.models import Carteira
from app.modules.assets.models import Ativo, AtivoCarteira
