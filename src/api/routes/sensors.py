import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.common.models import Sensor
from src.common.schemas import SensorCreate, SensorResponse

router = APIRouter(prefix="/api/v1/sensors", tags=["sensors"])

@router.post("/", response_model=SensorResponse)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@router.get("/", response_model=List[SensorResponse])
def list_sensors(
    asset_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Sensor)
    if asset_id:
        query = query.filter(Sensor.asset_id == asset_id)
    return query.all()

@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(sensor_id: uuid.UUID, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor