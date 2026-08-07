import os
import pandas as pd
from src.features.rolling_features import compute_rolling_features, compute_health_features, compute_seasonal_detrend_features
from src.models.anomaly.isolation_forest import IsolationForestAnomalyDetector

MODEL_DIR = "src/models/anomaly/artifacts"

def prepare_features(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df = compute_rolling_features(df, value_col="vibration_rms_mm_s")
    df = compute_rolling_features(df, value_col="temperature_celsius")
    df = compute_health_features(df)
    df = compute_seasonal_detrend_features(df, value_col="vibration_rms_mm_s")
    df = compute_seasonal_detrend_features(df, value_col="temperature_celsius")
    df = df.dropna(subset=[
        "vibration_rms_mm_s_diff_zscore",
        "temperature_celsius_diff_zscore"
    ]).reset_index(drop=True)
    return df

def train_and_evaluate(csv_path: str, model_name: str = "isolation_forest_v1"):
    print(f"Loading and preparing features from {csv_path} ...")
    df = prepare_features(csv_path)

    print("Training Isolation Forest ...")
    detector = IsolationForestAnomalyDetector(contamination=0.024)
    detector.fit(df)

    print("Predicting anomalies ...")
    results = detector.predict(df)

    # Evaluate against ground truth
    if "ground_truth_label" in results.columns:
        true_anomaly = results["ground_truth_label"] != "normal"
        predicted_anomaly = results["is_anomaly"]

        tp = ((true_anomaly) & (predicted_anomaly)).sum()
        fp = ((~true_anomaly) & (predicted_anomaly)).sum()
        fn = ((true_anomaly) & (~predicted_anomaly)).sum()
        tn = ((~true_anomaly) & (~predicted_anomaly)).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        print(f"\n=== Evaluation ===")
        print(f"True Positives: {tp}, False Positives: {fp}, False Negatives: {fn}, True Negatives: {tn}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall: {recall:.3f}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    detector.save(model_path)
    print(f"\nModel saved to {model_path}")

    return detector, results

if __name__ == "__main__":
    train_and_evaluate("data/synthetic/Motor_07_30days.csv")