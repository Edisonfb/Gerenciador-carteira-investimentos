"""Rotas HTTP do modulo de ativos financeiros."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.modules.assets.models import Asset
from app.modules.assets.schemas import AssetCreate, AssetResponse, AssetUpdate
from app.modules.assets.service import AssetService
from app.modules.auth.models import User

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse])
def list_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Asset]:
    _ = current_user
    return AssetService(db).list_assets()


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    _ = current_user
    return AssetService(db).get_asset(asset_id)


@router.post("", response_model=AssetResponse, status_code=201)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    _ = current_user
    return AssetService(db).create_asset(payload)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    _ = current_user
    return AssetService(db).update_asset(asset_id, payload)


@router.delete("/{asset_id}", response_model=AssetResponse)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    _ = current_user
    return AssetService(db).delete_asset(asset_id)
