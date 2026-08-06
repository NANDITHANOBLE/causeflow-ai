import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Numeric, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.common.database import Base

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