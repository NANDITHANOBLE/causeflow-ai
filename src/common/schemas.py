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

class SensorBase(BaseModel):
    sensor_name: str
    sensor_type: str
    unit: Optional[str] = None
    min_valid_value: Optional[float] = None
    max_valid_value: Optional[float] = None
    sampling_interval_seconds: Optional[int] = None
    is_active: Optional[bool] = True
    asset_id: Optional[uuid.UUID] = None

class SensorCreate(SensorBase):
    pass

class SensorResponse(SensorBase):
    sensor_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class TelemetryEventBase(BaseModel):
    timestamp: datetime
    sensor_id: uuid.UUID
    asset_id: uuid.UUID
    value: float
    quality_flag: Optional[str] = "valid"
    ingestion_source: Optional[str] = None
    metadata_json: Optional[dict] = None

class TelemetryEventCreate(TelemetryEventBase):
    pass

class TelemetryEventResponse(TelemetryEventBase):
    event_id: uuid.UUID

    class Config:
        from_attributes = True