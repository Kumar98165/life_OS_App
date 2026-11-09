"""LifeOS - Evaluation Engine and Benchmark Runner (Step 9).

Executes automated benchmarks against local or fine-tuned Ollama models:
- Validates model availability
- Measures response latency & tokens per second
- Runs deterministic metric calculators
- Aggregates individual and category scores
- Generates reproducible evaluation report snapshots
"""
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import requests

from app.ai.config import get_ai_config, check_ollama_health
from app.ai.evaluation.benchmark import BenchmarkDataset
from app.ai.evaluation.metrics import MetricsCalculator, EvaluatedCaseResult, EvaluationMetricResult


class ModelEvaluator:
    """Automated benchmark executor for LifeOS LLM models."""

    def __init__(
        self,
        target_model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        cfg = get_ai_config()
        self.target_model = target_model or cfg["model"]
        self.base_url = (base_url or cfg["base_url"]).rstrip("/")
        self.timeout = timeout

    def check_target_model_availability(self) -> Dict[str, Any]:
        """Verify if target model is present in Ollama runtime."""
        tags_url = f"{self.base_url}/api/tags"
        try:
            resp = requests.get(tags_url, timeout=self.timeout)
            if resp.status_code != 200:
                return {
                    "available": False,
                    "error": f"Ollama HTTP {resp.status_code}",
                    "models": []
                }
            data = resp.json()
            available_models = [m.get("name", "") for m in data.get("models", [])]
            is_available = any(
                self.target_model == m or self.target_model == m.split(":")[0] or m.startswith(self.target_model)
                for m in available_models
            )
            return {
                "available": is_available,
                "error": None if is_available else f"Model '{self.target_model}' not found in Ollama runtime.",
                "models": available_models
            }
        except Exception as e:
            return {
                "available": False,
                "error": f"Cannot connect to Ollama runtime at {self.base_url}: {str(e)}",
                "models": []
            }

    def evaluate_item(
        self,
        benchmark_item: Dict[str, Any],
        dry_run_mock_response: Optional[str] = None
    ) -> EvaluatedCaseResult:
        """Run a single benchmark test item through the model and score output."""
        test_id = benchmark_item["id"]
        category = benchmark_item["category"]
        prompt = benchmark_item["prompt"]
        context = benchmark_item.get("context")
        expected_keywords = benchmark_item.get("expected_keywords", [])
        min_length_chars = benchmark_item.get("min_length_chars", 30)

        # Build full prompt
        system_instruction = (
            "You are LifeOS, an intelligent, empathetic, and highly disciplined personal operating system assistant. "
            "Follow all formatting constraints accurately."
        )
        user_message = f"Context: {context}\n\nTask: {prompt}" if context else prompt

        response_text = ""
        latency_ms = 0.0
        token_count = 0
        tokens_per_sec = 0.0
        is_success = False
        error_msg = None

        if dry_run_mock_response is not None:
            # Mock mode for dry-run or unit testing
            response_text = dry_run_mock_response
            latency_ms = 45.0
            token_count = len(response_text.split())
            tokens_per_sec = 25.0
            is_success = True
        else:
            # Execute actual call to Ollama generate API
            endpoint = f"{self.base_url}/api/generate"
            payload = {
                "model": self.target_model,
                "prompt": f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n",
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for benchmark reproducibility
                    "num_predict": 512,
                }
            }

            start_t = time.perf_counter()
            try:
                resp = requests.post(endpoint, json=payload, timeout=self.timeout)
                latency_ms = round((time.perf_counter() - start_t) * 1000, 2)

                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "").strip()
                    eval_count = data.get("eval_count", 0)
                    eval_duration_ns = data.get("eval_duration", 1)

                    token_count = eval_count or len(response_text.split())
                    if eval_duration_ns > 0:
                        tokens_per_sec = round((eval_count / (eval_duration_ns / 1e9)), 2)
                    else:
                        tokens_per_sec = round((token_count / (latency_ms / 1000)), 2)

                    is_success = True
                else:
                    error_msg = f"Ollama HTTP {resp.status_code}: {resp.text}"
            except Exception as e:
                latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
                error_msg = str(e)

        # Calculate metrics
        m_relevance = MetricsCalculator.calculate_answer_relevance(response_text, expected_keywords)
        m_instruction = MetricsCalculator.calculate_instruction_following(response_text, benchmark_item)
        m_completeness = MetricsCalculator.calculate_response_completeness(response_text, min_length_chars)
        m_context = MetricsCalculator.calculate_context_utilization(response_text, context)

        metrics_map = {
            "answer_relevance": m_relevance,
            "instruction_following": m_instruction,
            "response_completeness": m_completeness,
            "context_utilization": m_context,
        }

        # Overall composite score: weighted average
        overall = round(
            (m_relevance.score * 0.35) +
            (m_instruction.score * 0.35) +
            (m_completeness.score * 0.15) +
            (m_context.score * 0.15),
            2
        )

        return EvaluatedCaseResult(
            test_id=test_id,
            category=category,
            prompt=prompt,
            context=context,
            response_text=response_text,
            latency_ms=latency_ms,
            token_count=token_count,
            tokens_per_sec=tokens_per_sec,
            is_success=is_success and error_msg is None,
            error=error_msg,
            metrics=metrics_map,
            overall_score=overall,
        )

    def run_benchmark(
        self,
        category: Optional[str] = None,
        mock_responses: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute full benchmark evaluation run and compile structured report."""
        start_run = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()

        # Check model availability unless mocking
        if mock_responses is None:
            avail = self.check_target_model_availability()
            if not avail["available"]:
                return {
                    "status": "failed",
                    "error": avail["error"],
                    "model_name": self.target_model,
                    "available_models": avail.get("models", []),
                    "started_at": started_at,
                    "benchmark_version": BenchmarkDataset.get_version(),
                }

        items = (
            BenchmarkDataset.get_items_by_category(category)
            if category
            else BenchmarkDataset.get_all_items()
        )

        case_results: List[EvaluatedCaseResult] = []
        failed_cases: List[Dict[str, Any]] = []

        total_latency = 0.0
        total_tokens = 0
        total_score = 0.0

        for item in items:
            mock_resp = mock_responses.get(item["id"]) if mock_responses else None
            case_eval = self.evaluate_item(item, dry_run_mock_response=mock_resp)
            case_results.append(case_eval)

            total_latency += case_eval.latency_ms
            total_tokens += case_eval.token_count
            total_score += case_eval.overall_score

            if not case_eval.is_success or case_eval.overall_score < 0.65:
                failed_cases.append({
                    "id": case_eval.test_id,
                    "category": case_eval.category,
                    "score": case_eval.overall_score,
                    "error": case_eval.error,
                    "reasoning": [m.reasoning for m in case_eval.metrics.values() if not m.passed]
                })

        count = len(case_results)
        avg_score = round(total_score / max(count, 1), 3)
        avg_latency = round(total_latency / max(count, 1), 2)
        total_duration_sec = round(time.perf_counter() - start_run, 2)
        throughput = round(total_tokens / max(total_duration_sec, 0.001), 2)

        # Aggregate category breakdown
        categories_breakdown: Dict[str, Dict[str, Any]] = {}
        for c in case_results:
            cat = c.category
            if cat not in categories_breakdown:
                categories_breakdown[cat] = {"count": 0, "total_score": 0.0, "passes": 0}
            categories_breakdown[cat]["count"] += 1
            categories_breakdown[cat]["total_score"] += c.overall_score
            if c.overall_score >= 0.65:
                categories_breakdown[cat]["passes"] += 1

        category_summary = {
            cat: {
                "count": data["count"],
                "avg_score": round(data["total_score"] / data["count"], 2),
                "pass_rate": round(data["passes"] / data["count"], 2),
            }
            for cat, data in categories_breakdown.items()
        }

        report = {
            "status": "completed",
            "model_name": self.target_model,
            "benchmark_version": BenchmarkDataset.get_version(),
            "benchmark_checksum": BenchmarkDataset.compute_checksum(),
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "execution_duration_sec": total_duration_sec,
            "total_test_cases": count,
            "passed_test_cases": count - len(failed_cases),
            "failed_test_cases_count": len(failed_cases),
            "aggregate_metrics": {
                "overall_score": avg_score,
                "pass_rate": round((count - len(failed_cases)) / max(count, 1), 2),
                "average_latency_ms": avg_latency,
                "tokens_per_second": throughput,
            },
            "category_summary": category_summary,
            "failed_cases": failed_cases,
            "individual_results": [c.model_dump() for c in case_results],
        }

        return report
