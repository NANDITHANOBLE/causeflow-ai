import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.common.models import TelemetryEvent
from src.common.schemas import TelemetryEventCreate, TelemetryEventResponse

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])

@router.post("/", response_model=TelemetryEventResponse)
def create_telemetry_event(event: TelemetryEventCreate, db: Session = Depends(get_db)):
    db_event = TelemetryEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[TelemetryEventResponse])
def query_telemetry(
    asset_id: Optional[uuid.UUID] = None,
    sensor_id: Optional[uuid.UUID] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TelemetryEvent)
    if asset_id:
        query = query.filter(TelemetryEvent.asset_id == asset_id)
    if sensor_id:
        query = query.filter(TelemetryEvent.sensor_id == sensor_id)
    if start:
        query = query.filter(TelemetryEvent.timestamp >= start)
    if end:
        query = query.filter(TelemetryEvent.timestamp <= end)
    return query.order_by(TelemetryEvent.timestamp.desc()).limit(500).all()