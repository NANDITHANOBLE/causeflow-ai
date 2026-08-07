import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Numeric, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.common.database import Base
from sqlalchemy import Boolean, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB

class Sensor(Base):
    __tablename__ = "sensors"

    sensor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.asset_id"))
    sensor_name = Column(String(255), nullable=False)
    sensor_type = Column(String(100), nullable=False)
    unit = Column(String(32))
    min_valid_value = Column(Numeric)
    max_valid_value = Column(Numeric)
    sampling_interval_seconds = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.sensor_id"))
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.asset_id"))
    value = Column(Float, nullable=False)
    quality_flag = Column(String(30), default="valid")
    ingestion_source = Column(String(50))
    metadata_json = Column("metadata", JSONB)

class Plant(Base):
    __tablename__ = "plants"

    plant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_name = Column(String(255), nullable=False)
    location = Column(String(255))
    timezone = Column(String(64), default="UTC")
    created_at = Column(TIMESTAMP, server_default=func.now())

class ProductionLine(Base):
    __tablename__ = "production_lines"

    line_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_id = Column(UUID(as_uuid=True), ForeignKey("plants.plant_id"))
    line_name = Column(String(255), nullable=False)
    product_type = Column(String(255))
    max_capacity_per_hour = Column(Integer)
    status = Column(String(50), default="active")
    created_at = Column(TIMESTAMP, server_default=func.now())

class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line_id = Column(UUID(as_uuid=True), ForeignKey("production_lines.line_id"))
    asset_name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)
    manufacturer = Column(String(255))
    model_number = Column(String(255))
    installation_date = Column(Date)
    criticality_score = Column(Numeric(4, 2))
    operational_status = Column(String(50), default="active")
    created_at = Column(TIMESTAMP, server_default=func.now())

class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.asset_id"))
    detected_at = Column(TIMESTAMP(timezone=True), nullable=False)
    model_name = Column(String(100))
    model_version = Column(String(100))
    anomaly_score = Column(Numeric(8, 5))
    severity = Column(String(20))
    affected_features = Column(JSONB)
    status = Column(String(30), default="open")
    created_at = Column(TIMESTAMP, server_default=func.now())