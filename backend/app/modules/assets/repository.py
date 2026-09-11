"""Acesso a dados do modulo de ativos financeiros."""

from sqlalchemy.orm import Session

from app.modules.assets.models import Asset


class AssetRepository:
    """Operacoes de persistencia de ativos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Asset]:
        return self.db.query(Asset).order_by(Asset.symbol.asc()).all()

    def get_by_id(self, asset_id: int) -> Asset | None:
        return self.db.get(Asset, asset_id)

    def get_by_symbol(self, symbol: str) -> Asset | None:
        return self.db.query(Asset).filter(Asset.symbol == symbol).first()

    def create(self, symbol: str, name: str, asset_type: str) -> Asset:
        asset = Asset(symbol=symbol, name=name, asset_type=asset_type)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def update(self, asset: Asset) -> Asset:
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def deactivate(self, asset: Asset) -> Asset:
        asset.is_active = False
        return self.update(asset)
