from datetime import datetime
import os
from src.simulation.sensor_generator import generate_motor_data
from src.simulation.incident_injector import inject_bearing_wear, inject_cooling_blockage

OUTPUT_DIR = "data/synthetic"

def generate_30_days_for_motor(asset_name: str, seed: int = 42):
    df = generate_motor_data(
        start_time=datetime(2026, 7, 1, 0, 0, 0),
        duration_hours=24 * 30,   # 30 days
        interval_seconds=60,       # 1 reading per minute
        seed=seed
    )

    total_points = len(df)

    # Inject bearing wear around day 10 (index ~ 10*1440)
    bearing_start = 10 * 1440
    df = inject_bearing_wear(df, start_index=bearing_start, duration_points=500, seed=seed + 1)

    # Inject cooling blockage around day 20
    cooling_start = 20 * 1440
    df = inject_cooling_blockage(df, start_index=cooling_start, duration_points=400, seed=seed + 2)

    df["asset_name"] = asset_name
    return df

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    assets = [
        {"asset_name": "Motor_07", "seed": 42},
        {"asset_name": "Motor_12", "seed": 84},
    ]

    for asset in assets:
        df = generate_30_days_for_motor(asset["asset_name"], seed=asset["seed"])
        output_path = os.path.join(OUTPUT_DIR, f"{asset['asset_name']}_30days.csv")
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} rows for {asset['asset_name']} -> {output_path}")
        print(f"Label distribution:\n{df['ground_truth_label'].value_counts()}\n")

if __name__ == "__main__":
    main()