import numpy as np
import pandas as pd

def inject_bearing_wear(
    df: pd.DataFrame,
    start_index: int,
    duration_points: int,
    seed: int = 42
) -> pd.DataFrame:
    """
    Simulates bearing degradation: vibration rises first, then temperature follows.
    Ground truth root cause: bearing_wear
    """
    rng = np.random.default_rng(seed)
    df = df.copy()
    end_index = min(start_index + duration_points, len(df))

    progress = np.linspace(0, 1, end_index - start_index)

    # Vibration increases up to 41% (matches blueprint example)
    vibration_increase = progress * 0.41 * df.loc[start_index:end_index - 1, "vibration_rms_mm_s"].mean()
    df.loc[start_index:end_index - 1, "vibration_rms_mm_s"] += vibration_increase

    # Temperature rises ~15-20 steps after vibration (lag effect)
    lag = 15
    temp_start = min(start_index + lag, len(df) - 1)
    temp_end = min(temp_start + duration_points, len(df))
    temp_progress = np.linspace(0, 1, temp_end - temp_start)
    temp_increase = temp_progress * 6.2  # matches blueprint: "rose 6.2°C"
    df.loc[temp_start:temp_end - 1, "temperature_celsius"] += temp_increase

    df["ground_truth_label"] = "normal"
    df.loc[start_index:end_index - 1, "ground_truth_label"] = "bearing_wear"

    return df

def inject_cooling_blockage(
    df: pd.DataFrame,
    start_index: int,
    duration_points: int,
    seed: int = 43
) -> pd.DataFrame:
    """
    Simulates cooling flow reduction: temperature rises, defect-relevant conditions increase.
    Ground truth root cause: cooling_efficiency_drop
    """
    df = df.copy()
    end_index = min(start_index + duration_points, len(df))

    progress = np.linspace(0, 1, end_index - start_index)
    temp_increase = progress * 10.0  # gradual overheating due to poor cooling

    df.loc[start_index:end_index - 1, "temperature_celsius"] += temp_increase

    df["ground_truth_label"] = df.get("ground_truth_label", pd.Series(["normal"] * len(df)))
    df.loc[start_index:end_index - 1, "ground_truth_label"] = "cooling_efficiency_drop"

    return df