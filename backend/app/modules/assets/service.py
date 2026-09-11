"""Regras de negocio do modulo de ativos financeiros."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ProjectException
from app.modules.assets.models import Asset
from app.modules.assets.repository import AssetRepository
from app.modules.assets.schemas import AssetCreate, AssetUpdate
from app.shared.validators import is_valid_asset_type


class AssetService:
    """Regras de gerenciamento de ativos."""

    def __init__(self, db: Session) -> None:
        self.repository = AssetRepository(db)

    def list_assets(self) -> list[Asset]:
        return self.repository.list_all()

    def get_asset(self, asset_id: int) -> Asset:
        asset = self.repository.get_by_id(asset_id)
        if asset is None:
            raise NotFoundError("Ativo nao encontrado.")
        return asset

    def create_asset(self, data: AssetCreate) -> Asset:
        symbol = data.symbol.strip().upper()
        asset_type = data.asset_type.strip().lower()

        if not is_valid_asset_type(asset_type):
            raise ProjectException("Tipo de ativo invalido.")

        if self.repository.get_by_symbol(symbol) is not None:
            raise ConflictError("Simbolo ja cadastrado.")

        return self.repository.create(
            symbol=symbol,
            name=data.name.strip(),
            asset_type=asset_type,
        )

    def update_asset(self, asset_id: int, data: AssetUpdate) -> Asset:
        asset = self.get_asset(asset_id)

        if data.symbol is not None:
            symbol = data.symbol.strip().upper()
            existing = self.repository.get_by_symbol(symbol)
            if existing is not None and existing.id != asset.id:
                raise ConflictError("Simbolo ja cadastrado.")
            asset.symbol = symbol

        if data.name is not None:
            asset.name = data.name.strip()

        if data.asset_type is not None:
            asset_type = data.asset_type.strip().lower()
            if not is_valid_asset_type(asset_type):
                raise ProjectException("Tipo de ativo invalido.")
            asset.asset_type = asset_type

        if data.is_active is not None:
            asset.is_active = data.is_active

        return self.repository.update(asset)

    def delete_asset(self, asset_id: int) -> Asset:
        asset = self.get_asset(asset_id)
        return self.repository.deactivate(asset)
