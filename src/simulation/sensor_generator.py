import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_motor_data(
    start_time: datetime,
    duration_hours: int = 24,
    interval_seconds: int = 60,
    base_temperature: float = 60.0,
    base_vibration: float = 3.0,
    base_current: float = 12.0,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates synthetic healthy sensor data for a motor asset.
    Simulates temperature, vibration, and current with realistic noise and daily cycles.
    """
    rng = np.random.default_rng(seed)

    num_points = int((duration_hours * 3600) / interval_seconds)
    timestamps = [start_time + timedelta(seconds=i * interval_seconds) for i in range(num_points)]

    hours_of_day = np.array([t.hour + t.minute / 60 for t in timestamps])
    daily_cycle = np.sin((hours_of_day / 24) * 2 * np.pi)

    temperature = base_temperature + 3 * daily_cycle + rng.normal(0, 0.8, num_points)
    vibration = base_vibration + 0.3 * daily_cycle + rng.normal(0, 0.15, num_points)
    current = base_current + 1.0 * daily_cycle + rng.normal(0, 0.3, num_points)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature_celsius": temperature.round(2),
        "vibration_rms_mm_s": vibration.round(3),
        "motor_current_amp": current.round(2)
    })

    return df