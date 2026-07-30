import base64
import io
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import IsolationForest
from scipy.spatial.distance import mahalanobis


class BaselineProfiler:
    """Builds and serializes agent-specific statistical baseline profiles."""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination

    def fit_baseline(self, feature_matrix: List[List[float]]) -> Tuple[List[float], List[List[float]], str]:
        """
        Fits Isolation Forest and Mahalanobis baseline parameters on synthetic normal feature matrix.
        Returns:
            (feature_means, feature_covariance, serialized_isolation_forest)
        """
        X = np.array(feature_matrix, dtype=np.float64)

        if X.shape[0] < 5:
            # Padding if scenario count is small during quick tests
            pad = np.zeros((10 - X.shape[0], X.shape[1]))
            X = np.vstack([X, pad])

        # 1. Feature Means
        means = np.mean(X, axis=0).tolist()

        # 2. Covariance Matrix (with regularization to prevent singular matrix)
        cov = np.cov(X, rowvar=False)
        cov += np.eye(X.shape[1]) * 1e-5
        covariance = cov.tolist()

        # 3. Isolation Forest Model
        iso_forest = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        iso_forest.fit(X)

        # Serialize Isolation Forest model to Base64 string
        buffer = io.BytesIO()
        joblib.dump(iso_forest, buffer)
        serialized_model = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return means, covariance, serialized_model

    @staticmethod
    def load_isolation_forest(serialized_model: str) -> IsolationForest:
        """Deserializes Isolation Forest model from Base64 string."""
        raw_bytes = base64.b64decode(serialized_model)
        buffer = io.BytesIO(raw_bytes)
        return joblib.load(buffer)
