from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.common.database import get_db

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "causeflow-api",
        "version": "1.0.0"
    }

@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }