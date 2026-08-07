import pandas as pd
import numpy as np

def compute_rolling_features(
    df: pd.DataFrame,
    value_col: str,
    timestamp_col: str = "timestamp",
    windows: dict = None
) -> pd.DataFrame:
    """
    Computes rolling statistical features for a single sensor value column.
    windows: dict mapping a label to a window size in number of points, e.g.
        {"5m": 5, "30m": 30, "2h": 120, "24h": 1440}
    Assumes df is sorted by timestamp and has 1-minute interval data (adjust windows accordingly).
    """
    if windows is None:
        windows = {"5m": 5, "30m": 30, "2h": 120, "24h": 1440}

    df = df.sort_values(timestamp_col).reset_index(drop=True)
    result = df.copy()

    baseline_mean = df[value_col].mean()
    baseline_std = df[value_col].std() if df[value_col].std() > 0 else 1e-6

    for label, window in windows.items():
        roll = df[value_col].rolling(window=window, min_periods=1)

        result[f"{value_col}_mean_{label}"] = roll.mean()
        result[f"{value_col}_std_{label}"] = roll.std().fillna(0)
        result[f"{value_col}_min_{label}"] = roll.min()
        result[f"{value_col}_max_{label}"] = roll.max()

        # Rate of change / slope over the window
        result[f"{value_col}_slope_{label}"] = (
            df[value_col] - df[value_col].shift(window)
        ) / window

        # Exponentially weighted moving average
        result[f"{value_col}_ewma_{label}"] = df[value_col].ewm(span=window, adjust=False).mean()

    # Z-score against global baseline
    result[f"{value_col}_zscore"] = (df[value_col] - baseline_mean) / baseline_std

    # Rate of change over 1 step (instantaneous)
    result[f"{value_col}_diff_1"] = df[value_col].diff().fillna(0)

    return result

def compute_health_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes cross-feature health ratios, assuming columns:
    temperature_celsius, vibration_rms_mm_s, motor_current_amp exist.
    """
    df = df.copy()

    if "vibration_rms_mm_s" in df.columns and "motor_current_amp" in df.columns:
        df["vibration_to_current_ratio"] = df["vibration_rms_mm_s"] / df["motor_current_amp"].replace(0, np.nan)

    if "temperature_celsius" in df.columns:
        df["temperature_change_15m"] = df["temperature_celsius"].diff(15).fillna(0)

    return df