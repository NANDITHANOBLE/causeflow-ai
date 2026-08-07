import uuid
import pandas as pd
from sqlalchemy.orm import Session
from src.common.models import TelemetryEvent, Sensor, Anomaly
from src.models.anomaly.isolation_forest import IsolationForestAnomalyDetector
from src.features.rolling_features import (
    compute_rolling_features,
    compute_health_features,
    compute_seasonal_detrend_features,
)

MODEL_PATH = "src/models/anomaly/artifacts/isolation_forest_v1.joblib"

_model_cache = None

def get_model() -> IsolationForestAnomalyDetector:
    global _model_cache
    if _model_cache is None:
        _model_cache = IsolationForestAnomalyDetector.load(MODEL_PATH)
    return _model_cache

def fetch_telemetry_as_wide_df(db: Session, asset_id: uuid.UUID, window_minutes: int = 5760) -> pd.DataFrame:
    """
    Fetches recent telemetry for an asset and pivots it into a wide dataframe
    with one column per sensor_type (e.g., vibration_rms_mm_s, temperature_celsius),
    which is the format our feature engineering functions expect.
    Needs enough history (default 4 days = 5760 min) to compute seasonal features.
    """
    sensors = db.query(Sensor).filter(Sensor.asset_id == asset_id).all()
    sensor_type_map = {s.sensor_id: s.sensor_type for s in sensors}

    events = (
        db.query(TelemetryEvent)
        .filter(TelemetryEvent.asset_id == asset_id)
        .order_by(TelemetryEvent.timestamp.desc())
        .limit(window_minutes * len(sensors) if sensors else window_minutes)
        .all()
    )

    if not events:
        return pd.DataFrame()

    rows = []
    for e in events:
        sensor_type = sensor_type_map.get(e.sensor_id, "unknown")
        rows.append({"timestamp": e.timestamp, "sensor_type": sensor_type, "value": e.value})

    long_df = pd.DataFrame(rows)
    wide_df = long_df.pivot_table(index="timestamp", columns="sensor_type", values="value").reset_index()
    wide_df = wide_df.sort_values("timestamp").reset_index(drop=True)

    return wide_df

def score_asset_anomalies(db: Session, asset_id: uuid.UUID, window_minutes: int = 5760) -> pd.DataFrame:
    df = fetch_telemetry_as_wide_df(db, asset_id, window_minutes)

    if df.empty or "vibration_rms_mm_s" not in df.columns or "temperature_celsius" not in df.columns:
        return pd.DataFrame()

    df = compute_rolling_features(df, value_col="vibration_rms_mm_s")
    df = compute_rolling_features(df, value_col="temperature_celsius")
    df = compute_health_features(df)
    df = compute_seasonal_detrend_features(df, value_col="vibration_rms_mm_s")
    df = compute_seasonal_detrend_features(df, value_col="temperature_celsius")

    df = df.dropna(subset=[
        "vibration_rms_mm_s_diff_zscore",
        "temperature_celsius_diff_zscore"
    ]).reset_index(drop=True)

    if df.empty:
        return df

    model = get_model()
    results = model.predict(df)
    return results

def persist_anomalies(db: Session, asset_id: uuid.UUID, results: pd.DataFrame, model_version: str = "isolation_forest_v1") -> int:
    anomaly_rows = results[results["is_anomaly"] == True]
    count = 0

    for _, row in anomaly_rows.iterrows():
        anomaly = Anomaly(
            asset_id=asset_id,
            detected_at=row["timestamp"],
            model_name="isolation_forest",
            model_version=model_version,
            anomaly_score=float(row["anomaly_score"]),
            severity="high" if row["anomaly_score"] > 0.7 else "medium",
            affected_features={
                "vibration_diff_zscore": float(row.get("vibration_rms_mm_s_diff_zscore", 0)),
                "temperature_diff_zscore": float(row.get("temperature_celsius_diff_zscore", 0)),
            },
            status="open"
        )
        db.add(anomaly)
        count += 1

    db.commit()
    return count