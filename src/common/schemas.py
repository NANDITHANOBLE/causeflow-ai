import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class AssetBase(BaseModel):
    asset_name: str
    asset_type: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    installation_date: Optional[date] = None
    criticality_score: Optional[float] = None
    operational_status: Optional[str] = "active"
    line_id: Optional[uuid.UUID] = None

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    asset_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True