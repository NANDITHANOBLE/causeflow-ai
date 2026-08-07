import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURE_COLUMNS = [
    "vibration_rms_mm_s_zscore",
    "vibration_rms_mm_s_mean_2h",
    "vibration_rms_mm_s_std_2h",
    "vibration_rms_mm_s_diff_zscore",
    "temperature_celsius_zscore",
    "temperature_celsius_mean_2h",
    "temperature_celsius_std_2h",
    "temperature_celsius_diff_zscore",
]

class IsolationForestAnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=200
        )
        self.feature_columns = FEATURE_COLUMNS
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        X = df[self.feature_columns].fillna(0)
        self.model.fit(X)
        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predicting.")

        X = df[self.feature_columns].fillna(0)

        raw_scores = self.model.decision_function(X)
        # Convert to a 0-1 anomaly score where higher = more anomalous
        anomaly_score = 1 - (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-9)

        predictions = self.model.predict(X)  # -1 = anomaly, 1 = normal
        is_anomaly = predictions == -1

        result = df.copy()
        result["anomaly_score"] = anomaly_score.round(4)
        result["is_anomaly"] = is_anomaly

        return result

    def save(self, path: str):
        joblib.dump(self, path)

    @staticmethod
    def load(path: str):
        return joblib.load(path)