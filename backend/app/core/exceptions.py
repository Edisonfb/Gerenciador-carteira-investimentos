"""Excecoes personalizadas compartilhadas pelo backend."""


class ProjectException(Exception):
    """Representa um erro de negocio conhecido dentro da aplicacao."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(ProjectException):
    """Recurso nao encontrado."""

    def __init__(self, message: str = "Recurso nao encontrado.") -> None:
        super().__init__(message=message, status_code=404)


class UnauthorizedError(ProjectException):
    """Usuario nao autenticado ou credenciais invalidas."""

    def __init__(self, message: str = "Nao autenticado.") -> None:
        super().__init__(message=message, status_code=401)


class ConflictError(ProjectException):
    """Conflito de dados (ex.: email ja cadastrado)."""

    def __init__(self, message: str = "Conflito de dados.") -> None:
        super().__init__(message=message, status_code=409)


class ForbiddenError(ProjectException):
    """Usuario sem permissao para a operacao."""

    def __init__(self, message: str = "Sem permissao.") -> None:
        super().__init__(message=message, status_code=403)
