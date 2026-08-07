import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.common.database import get_db
from src.services.anomaly_service import score_asset_anomalies, persist_anomalies

router = APIRouter(prefix="/api/v1/anomalies", tags=["anomalies"])

class AnalyzeRequest(BaseModel):
    asset_id: uuid.UUID
    window_minutes: int = 5760

@router.post("/analyze")
def analyze_asset(request: AnalyzeRequest, db: Session = Depends(get_db)):
    results = score_asset_anomalies(db, request.asset_id, request.window_minutes)

    if results.empty:
        raise HTTPException(
            status_code=400,
            detail="Not enough telemetry history to compute features (need at least ~4 days of data with vibration and temperature sensors)."
        )

    anomaly_count = int(results["is_anomaly"].sum())
    persisted = persist_anomalies(db, request.asset_id, results)

    latest = results.iloc[-1]

    return {
        "asset_id": str(request.asset_id),
        "total_points_analyzed": len(results),
        "anomalies_detected": anomaly_count,
        "anomalies_persisted": persisted,
        "latest_reading": {
            "timestamp": str(latest["timestamp"]),
            "anomaly_score": float(latest["anomaly_score"]),
            "is_anomaly": bool(latest["is_anomaly"])
        }
    }