import uuid
import pandas as pd
from sqlalchemy.orm import Session
from src.common.models import Asset, Sensor, TelemetryEvent

def get_or_create_asset(db: Session, asset_name: str, asset_type: str = "motor") -> uuid.UUID:
    asset = db.query(Asset).filter(Asset.asset_name == asset_name).first()
    if asset:
        return asset.asset_id

    asset = Asset(
        asset_name=asset_name,
        asset_type=asset_type,
        operational_status="active"
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset.asset_id

def get_or_create_sensor(db: Session, asset_id: uuid.UUID, sensor_name: str, sensor_type: str, unit: str) -> uuid.UUID:
    sensor = db.query(Sensor).filter(
        Sensor.asset_id == asset_id,
        Sensor.sensor_name == sensor_name
    ).first()
    if sensor:
        return sensor.sensor_id

    sensor = Sensor(
        asset_id=asset_id,
        sensor_name=sensor_name,
        sensor_type=sensor_type,
        unit=unit,
        is_active=True
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor.sensor_id

def load_csv_to_db(db: Session, csv_path: str, batch_size: int = 1000):
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    asset_name = df["asset_name"].iloc[0]

    asset_id = get_or_create_asset(db, asset_name)

    sensor_map = {
        "temperature_celsius": get_or_create_sensor(db, asset_id, f"{asset_name}_temperature", "temperature_celsius", "celsius"),
        "vibration_rms_mm_s": get_or_create_sensor(db, asset_id, f"{asset_name}_vibration", "vibration_rms_mm_s", "mm/s"),
        "motor_current_amp": get_or_create_sensor(db, asset_id, f"{asset_name}_current", "motor_current_amp", "amp"),
    }

    total_inserted = 0
    events = []

    for _, row in df.iterrows():
        for feature, sensor_id in sensor_map.items():
            events.append(TelemetryEvent(
                timestamp=row["timestamp"],
                sensor_id=sensor_id,
                asset_id=asset_id,
                value=float(row[feature]),
                quality_flag="valid",
                ingestion_source="csv_backfill",
                metadata_json={"ground_truth_label": row.get("ground_truth_label", "normal")}
            ))

        if len(events) >= batch_size:
            db.bulk_save_objects(events)
            db.commit()
            total_inserted += len(events)
            events = []

    if events:
        db.bulk_save_objects(events)
        db.commit()
        total_inserted += len(events)

    print(f"Inserted {total_inserted} telemetry events for {asset_name}")
    return total_inserted