import numpy as np
from typing import Dict, Any, List, Tuple
from scipy.spatial.distance import mahalanobis
from app.ml.baseline_profiler import BaselineProfiler
from app.ml.feature_extraction import FEATURE_NAMES
from app.config import settings


def compute_mahalanobis_distance(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    """Computes Mahalanobis Distance of observation vector x against baseline mean and covariance."""
    try:
        inv_cov = np.linalg.pinv(cov)
        dist = mahalanobis(x, mean, inv_cov)
        return float(dist)
    except Exception:
        return 0.0


class RealTimeAnomalyScorer:
    """Real-time anomaly scoring engine combining Isolation Forest & Mahalanobis Distance."""

    def score_turn(
        self,
        feature_vector: List[float],
        feature_means: List[float],
        feature_covariance: List[List[float]],
        serialized_iso_forest: str,
        threshold: float = settings.ANOMALY_THRESHOLD
    ) -> Dict[str, Any]:

        x = np.array(feature_vector, dtype=np.float64)
        means = np.array(feature_means, dtype=np.float64)
        cov = np.array(feature_covariance, dtype=np.float64)

        # 1. Isolation Forest Anomaly Score
        iso_forest = BaselineProfiler.load_isolation_forest(serialized_iso_forest)
        # raw decision_function: positive for inliers, negative for outliers
        raw_iso_score = float(iso_forest.decision_function([x])[0])
        # Transform decision function to normalized [0, 1] anomaly score (higher = more anomalous)
        iso_score = float(1.0 / (1.0 + np.exp(raw_iso_score * 4.0)))

        # 2. Mahalanobis Distance
        maha_dist = compute_mahalanobis_distance(x, means, cov)
        # Normalize Mahalanobis distance to [0, 1] scale using sigmoid-like scaling
        maha_score = float(1.0 - np.exp(-maha_dist / 8.0))

        # 3. Combined Score (Weighted Ensemble)
        combined_score = float(0.5 * iso_score + 0.5 * maha_score)

        # 4. Feature Attribution Calculation (Z-score contribution per feature)
        attribution = {}
        std_devs = np.sqrt(np.diag(cov))
        std_devs[std_devs == 0] = 1e-5

        z_scores = np.abs((x - means) / std_devs)
        total_z = np.sum(z_scores) + 1e-5

        for idx, fname in enumerate(FEATURE_NAMES):
            weight = float(z_scores[idx] / total_z)
            attribution[fname] = round(weight, 4)

        flagged = bool(combined_score >= threshold)

        return {
            "isolation_score": round(iso_score, 4),
            "mahalanobis_distance": round(maha_dist, 4),
            "combined_score": round(combined_score, 4),
            "flagged": flagged,
            "feature_attribution": attribution
        }


anomaly_scorer_instance = RealTimeAnomalyScorer()
