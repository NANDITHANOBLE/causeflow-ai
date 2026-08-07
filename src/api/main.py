from fastapi import FastAPI
from src.api.routes import health, assets, sensors, telemetry, anomalies

app = FastAPI(
    title="CauseFlow AI",
    description="AI platform for smart manufacturing anomaly detection, root-cause analysis, and safe recommendations",
    version="1.0.0"
)

app.include_router(health.router)
app.include_router(assets.router)
app.include_router(sensors.router)
app.include_router(telemetry.router)
app.include_router(anomalies.router)

@app.get("/")
def root():
    return {"message": "Welcome to CauseFlow AI"}