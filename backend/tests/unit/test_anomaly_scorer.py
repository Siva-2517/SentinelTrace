import random
import pytest
from app.ml.baseline_profiler import BaselineProfiler
from app.ml.anomaly_scorer import anomaly_scorer_instance


def test_baseline_profiler_and_scoring():
    # Synthetic normal feature matrix with realistic variance
    random.seed(42)
    normal_fv_list = []
    for _ in range(25):
        normal_fv_list.append([
            1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            float(random.randint(15, 30)),
            round(random.uniform(2.8, 3.8), 2),
            float(random.randint(80, 130)),
            float(random.randint(20, 50)),
            0.0, 0.0
        ])

    profiler = BaselineProfiler(contamination=0.1)
    means, cov, iso_serialized = profiler.fit_baseline(normal_fv_list)

    assert len(means) == 12
    assert len(cov) == 12

    # Score normal observation (falls well within normal variance bounds)
    normal_obs = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 22.0, 3.1, 105.0, 28.0, 0.0, 0.0]
    score_res = anomaly_scorer_instance.score_turn(normal_obs, means, cov, iso_serialized, threshold=0.65)
    assert "combined_score" in score_res
    assert score_res["combined_score"] < 0.65

    # Score anomalous observation (malicious injection pattern with multi-tool sequence and high entropy)
    anomalous_obs = [3.0, 1.0, 1.0, 0.0, 0.0, 0.0, 180.0, 5.8, 800.0, 250.0, 1.0, 2.5]
    anom_res = anomaly_scorer_instance.score_turn(anomalous_obs, means, cov, iso_serialized, threshold=0.65)
    assert anom_res["combined_score"] > score_res["combined_score"]
    assert anom_res["flagged"] is True

