import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.common.models import Asset
from src.common.schemas import AssetCreate, AssetResponse

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

@router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.get("/", response_model=List[AssetResponse])
def list_assets(
    line_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Asset)
    if line_id:
        query = query.filter(Asset.line_id == line_id)
    if status:
        query = query.filter(Asset.operational_status == status)
    return query.all()

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.delete("/{asset_id}")
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted successfully"}