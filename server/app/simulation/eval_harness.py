from typing import Dict, Any, List
import numpy as np
from app.agent.sample_agent import sample_agent_instance
from app.ml.feature_extraction import extract_turn_features
from app.ml.anomaly_scorer import anomaly_scorer_instance
from app.simulation.scenario_generator import generate_synthetic_scenarios
from app.simulation.injection_payloads import CRAFTED_INJECTION_PAYLOADS
from app.config import settings


class EvaluationHarness:
    """Evaluation framework computing Precision, Recall, FPR, ROC metrics and score calibration."""

    async def run_evaluation(
        self,
        baseline_means: List[float],
        baseline_covariance: List[List[float]],
        serialized_iso_forest: str,
        threshold: float = settings.ANOMALY_THRESHOLD
    ) -> Dict[str, Any]:

        normal_scenarios = generate_synthetic_scenarios(20)
        y_true = []
        y_scores = []
        y_pred = []
        scenario_results = []

        # 1. Evaluate Normal Scenarios (Ground Truth = 0)
        normal_scores_list = []
        for idx, prompt in enumerate(normal_scenarios):
            turn_res = await sample_agent_instance.execute_turn(prompt)
            fv = extract_turn_features(turn_res["tool_calls"])
            score_res = anomaly_scorer_instance.score_turn(
                fv, baseline_means, baseline_covariance, serialized_iso_forest, threshold
            )
            comb_score = score_res["combined_score"]
            is_flagged = score_res["flagged"]

            y_true.append(0)
            y_scores.append(comb_score)
            y_pred.append(1 if is_flagged else 0)
            normal_scores_list.append(comb_score)

            scenario_results.append({
                "scenario_id": f"normal_{idx+1}",
                "prompt": prompt,
                "label": 0,
                "score": comb_score,
                "flagged": is_flagged,
                "passed": not is_flagged
            })

        # 2. Evaluate Injected Scenarios (Ground Truth = 1)
        injected_scores_list = []
        for payload in CRAFTED_INJECTION_PAYLOADS:
            prompt = payload["user_prompt"]
            turn_res = await sample_agent_instance.execute_turn(prompt)
            fv = extract_turn_features(turn_res["tool_calls"])
            score_res = anomaly_scorer_instance.score_turn(
                fv, baseline_means, baseline_covariance, serialized_iso_forest, threshold
            )
            comb_score = score_res["combined_score"]
            is_flagged = score_res["flagged"]

            y_true.append(1)
            y_scores.append(comb_score)
            y_pred.append(1 if is_flagged else 0)
            injected_scores_list.append(comb_score)

            scenario_results.append({
                "scenario_id": payload["id"],
                "prompt": prompt,
                "label": 1,
                "score": comb_score,
                "flagged": is_flagged,
                "passed": is_flagged
            })

        # 3. Calculate Confusion Matrix & Metrics
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 1.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        # Calibration Check (Target: At least 2 normal runs score above median but below threshold)
        median_normal = float(np.median(normal_scores_list)) if normal_scores_list else 0.0
        normal_above_median_below_thresh = sum(
            1 for s in normal_scores_list if median_normal < s < threshold
        )
        is_calibrated = bool(normal_above_median_below_thresh >= 2)

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "false_positive_rate": round(fpr, 4),
            "threshold_used": threshold,
            "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
            "calibration": {
                "median_normal_score": round(median_normal, 4),
                "normal_runs_above_median_below_thresh": normal_above_median_below_thresh,
                "is_calibrated": is_calibrated
            },
            "results": scenario_results
        }


eval_harness_instance = EvaluationHarness()
