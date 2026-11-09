"""LifeOS - Model Comparison & Evaluation Reporting Service (Step 9).

Coordinates:
- Benchmark execution between models (e.g. qwen2.5:3b vs qwen2.5:3b-lifeos)
- Differential analysis across pillars and latency
- Safe persistence of evaluation reports without mutating production weights
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.ai.evaluation.evaluator import ModelEvaluator
from app.ai.evaluation.benchmark import BenchmarkDataset


class ModelEvaluationService:
    """Service handling model evaluation execution, comparison, and report management."""

    def __init__(self, reports_dir: str = "./evaluation_reports"):
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def evaluate_model(
        self,
        model_name: Optional[str] = None,
        mock_responses: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute evaluation run for a single model and save report."""
        evaluator = ModelEvaluator(target_model=model_name)
        report = evaluator.run_benchmark(mock_responses=mock_responses)

        if report.get("status") == "completed":
            self._save_report(report)

        return report

    def compare_models(
        self,
        base_model_name: str = "qwen2.5:3b",
        candidate_model_name: str = "qwen2.5:3b-lifeos",
        base_mock_responses: Optional[Dict[str, str]] = None,
        candidate_mock_responses: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Evaluate both base and candidate fine-tuned models and return structured differential analysis."""
        base_evaluator = ModelEvaluator(target_model=base_model_name)
        candidate_evaluator = ModelEvaluator(target_model=candidate_model_name)

        # 1. Evaluate base model
        base_report = base_evaluator.run_benchmark(mock_responses=base_mock_responses)
        if base_report.get("status") != "completed":
            return {
                "comparison_status": "failed",
                "error": f"Base model evaluation failed: {base_report.get('error')}",
                "base_model": base_model_name,
                "candidate_model": candidate_model_name,
            }

        # 2. Check candidate model availability
        if candidate_mock_responses is None:
            cand_avail = candidate_evaluator.check_target_model_availability()
            if not cand_avail["available"]:
                return {
                    "comparison_status": "candidate_unavailable",
                    "message": (
                        f"Candidate model '{candidate_model_name}' is not yet deployed or available in Ollama. "
                        "Base model evaluated successfully. Benchmark report generated."
                    ),
                    "base_model_report": base_report,
                    "candidate_model": candidate_model_name,
                    "available_models": cand_avail.get("models", [])
                }

        # 3. Evaluate candidate model
        candidate_report = candidate_evaluator.run_benchmark(mock_responses=candidate_mock_responses)
        if candidate_report.get("status") != "completed":
            return {
                "comparison_status": "candidate_failed",
                "error": candidate_report.get("error"),
                "base_model_report": base_report,
            }

        # 4. Compute comparative deltas
        base_metrics = base_report["aggregate_metrics"]
        cand_metrics = candidate_report["aggregate_metrics"]

        score_delta = round(cand_metrics["overall_score"] - base_metrics["overall_score"], 3)
        latency_delta = round(cand_metrics["average_latency_ms"] - base_metrics["average_latency_ms"], 2)
        pass_rate_delta = round(cand_metrics["pass_rate"] - base_metrics["pass_rate"], 2)

        # Category comparison
        category_deltas = {}
        for cat in BenchmarkDataset.get_all_items():
            category_name = cat["category"]
            base_cat = base_report["category_summary"].get(category_name, {})
            cand_cat = candidate_report["category_summary"].get(category_name, {})

            if base_cat and cand_cat:
                category_deltas[category_name] = {
                    "base_score": base_cat.get("avg_score", 0.0),
                    "candidate_score": cand_cat.get("avg_score", 0.0),
                    "delta": round(cand_cat.get("avg_score", 0.0) - base_cat.get("avg_score", 0.0), 3)
                }

        comparison_summary = {
            "comparison_status": "completed",
            "benchmark_version": BenchmarkDataset.get_version(),
            "benchmark_checksum": BenchmarkDataset.compute_checksum(),
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "base_model": {
                "name": base_model_name,
                "overall_score": base_metrics["overall_score"],
                "pass_rate": base_metrics["pass_rate"],
                "avg_latency_ms": base_metrics["average_latency_ms"],
            },
            "candidate_model": {
                "name": candidate_model_name,
                "overall_score": cand_metrics["overall_score"],
                "pass_rate": cand_metrics["pass_rate"],
                "avg_latency_ms": cand_metrics["average_latency_ms"],
            },
            "deltas": {
                "score_improvement": score_delta,
                "pass_rate_change": pass_rate_delta,
                "latency_change_ms": latency_delta,
            },
            "category_deltas": category_deltas,
            "promotion_recommendation": (
                "PASS: Candidate outperforms base model across benchmark."
                if score_delta > 0.0 and pass_rate_delta >= 0.0
                else "HOLD: Candidate does not demonstrate benchmark superiority."
            ),
        }

        # Save comparison report
        self._save_comparison_report(comparison_summary)

        return comparison_summary

    def _save_report(self, report: Dict[str, Any]) -> str:
        safe_model = report["model_name"].replace(":", "_").replace("/", "_")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"eval_{safe_model}_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return filepath

    def _save_comparison_report(self, comparison: Dict[str, Any]) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2)

        return filepath

