"""Unit and integration tests for LifeOS STEP 9 - AI Model Evaluation & Benchmarking."""

import os
import json
import pytest

from app.ai.evaluation.benchmark import BenchmarkDataset, BENCHMARK_ITEMS
from app.ai.evaluation.metrics import MetricsCalculator, EvaluationMetricResult
from app.ai.evaluation.evaluator import ModelEvaluator
from app.services.model_evaluation_service import ModelEvaluationService


class TestBenchmarkDataset:
    """Tests for benchmark dataset integrity, categories, and checksum verification."""

    def test_benchmark_has_9_core_pillars(self):
        items = BenchmarkDataset.get_all_items()
        assert len(items) >= 9

        categories = {item["category"] for item in items}
        expected_categories = {
            "daily_planning",
            "task_management",
            "goal_setting",
            "habit_coaching",
            "productivity_assistance",
            "instruction_following",
            "context_understanding",
            "response_accuracy",
            "personalization",
        }
        assert expected_categories.issubset(categories)

    def test_benchmark_item_structure_validity(self):
        for item in BenchmarkDataset.get_all_items():
            assert BenchmarkDataset.validate_item_structure(item) is True
            assert isinstance(item["id"], str)
            assert isinstance(item["prompt"], str)
            assert len(item["prompt"]) > 10
            assert isinstance(item["expected_keywords"], list)
            assert item["min_length_chars"] > 0

    def test_benchmark_checksum_reproducibility(self):
        hash1 = BenchmarkDataset.compute_checksum()
        hash2 = BenchmarkDataset.compute_checksum()
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_get_items_by_category(self):
        planning_items = BenchmarkDataset.get_items_by_category("daily_planning")
        assert len(planning_items) >= 2
        for item in planning_items:
            assert item["category"] == "daily_planning"


class TestMetricsCalculator:
    """Tests for deterministic scoring calculations without LLM dependency."""

    def test_answer_relevance_keyword_matching(self):
        resp = "I have scheduled your 9:00 AM focus block before lunch."
        res = MetricsCalculator.calculate_answer_relevance(resp, ["9:00", "lunch", "focus"])
        assert res.score == 1.0
        assert res.passed is True

        partial_resp = "I have scheduled your 9:00 AM meeting."
        partial_res = MetricsCalculator.calculate_answer_relevance(partial_resp, ["9:00", "lunch", "focus"])
        assert partial_res.score == 0.33
        assert partial_res.passed is False

    def test_instruction_following_negative_constraints(self):
        item = {
            "must_not_contain": ["in conclusion", "here are"],
            "required_structure": "strict_numbered_list",
        }

        # Violates negative constraint
        resp_violating = "Here are the benefits: 1. Focus 2. Clarity 3. Output"
        res_violating = MetricsCalculator.calculate_instruction_following(resp_violating, item)
        assert res_violating.score < 1.0
        assert "Violated negative constraints" in res_violating.reasoning

        # Fully compliant
        resp_clean = "1. Focus\n2. Clarity\n3. Output"
        res_clean = MetricsCalculator.calculate_instruction_following(resp_clean, item)
        assert res_clean.score >= 0.9
        assert res_clean.passed is True

    def test_response_completeness(self):
        res = MetricsCalculator.calculate_response_completeness("A short text.", min_length_chars=50)
        assert res.passed is False
        assert res.score < 0.7

        long_text = "This is a comprehensive response that easily exceeds fifty characters in length."
        res_pass = MetricsCalculator.calculate_response_completeness(long_text, min_length_chars=50)
        assert res_pass.passed is True
        assert res_pass.score == 1.0

    def test_context_utilization(self):
        context = "User profile: Software developer, works from 10:00 to 18:00, avoids morning meetings."
        good_response = "As a software developer working until 18:00, you should avoid morning meetings."
        res = MetricsCalculator.calculate_context_utilization(good_response, context)
        assert res.score > 0.0
        assert res.passed is True


class TestModelEvaluator:
    """Tests for benchmark runner and Ollama offline/mocking handling."""

    def test_missing_or_unreachable_ollama_handling(self):
        evaluator = ModelEvaluator(
            target_model="non_existent_model_123",
            base_url="http://localhost:9999"  # invalid port
        )
        report = evaluator.run_benchmark()
        assert report["status"] == "failed"
        assert "unreachable" in report["error"].lower() or "connect" in report["error"].lower()

    def test_mock_benchmark_execution(self):
        evaluator = ModelEvaluator(target_model="qwen2.5:3b")

        mock_responses = {
            item["id"]: (
                f"1. Focus time at 9:00 with lunch break. "
                f"2. Urgent production crash is Quadrant 1, spam is Quadrant 3. "
                f"3. Water habit cue routine reward with specific measurable SMART milestones. "
                f"4. Pomodoro 25 minutes with 5 minute break. {item['prompt']}"
            )
            for item in BenchmarkDataset.get_all_items()
        }

        report = evaluator.run_benchmark(mock_responses=mock_responses)
        assert report["status"] == "completed"
        assert report["model_name"] == "qwen2.5:3b"
        assert report["total_test_cases"] == len(BenchmarkDataset.get_all_items())
        assert report["aggregate_metrics"]["overall_score"] > 0.6
        assert "category_summary" in report
        assert len(report["individual_results"]) == len(BenchmarkDataset.get_all_items())


class TestModelComparisonService:
    """Tests for comparative evaluation between base model and fine-tuned candidates."""

    def test_candidate_unavailable_handled_safely(self, tmp_path):
        service = ModelEvaluationService(reports_dir=str(tmp_path))

        base_mocks = {
            item["id"]: f"Base model answer with 9:00 lunch focus 1. 2. 3. for {item['prompt']}"
            for item in BenchmarkDataset.get_all_items()
        }

        # Compare with non-deployed fine-tuned model (no candidate mocks)
        res = service.compare_models(
            base_model_name="qwen2.5:3b",
            candidate_model_name="qwen2.5:3b-lifeos-not-deployed",
            base_mock_responses=base_mocks,
            candidate_mock_responses=None
        )

        assert res["comparison_status"] == "candidate_unavailable"
        assert "not yet deployed" in res["message"]
        assert "base_model_report" in res

    def test_full_model_comparison_with_deltas(self, tmp_path):
        service = ModelEvaluationService(reports_dir=str(tmp_path))

        base_mocks = {
            item["id"]: f"Adequate basic response {item['prompt']}"
            for item in BenchmarkDataset.get_all_items()
        }
        # Candidate has superior formatting and keyword precision
        cand_mocks = {
            item["id"]: (
                f"1. 9:00 AM lunch focus block. 2. Quadrant 3 urgent spam. "
                f"3. Specific measurable SMART milestones water habit cue routine reward. "
                f"4. 25 minutes pomodoro with 5 break. Detailed answer for {item['prompt']}"
            )
            for item in BenchmarkDataset.get_all_items()
        }

        comparison = service.compare_models(
            base_model_name="qwen2.5:3b",
            candidate_model_name="qwen2.5:3b-lifeos",
            base_mock_responses=base_mocks,
            candidate_mock_responses=cand_mocks,
        )

        assert comparison["comparison_status"] == "completed"
        assert "deltas" in comparison
        assert "score_improvement" in comparison["deltas"]
        assert comparison["deltas"]["score_improvement"] >= 0.0
        assert "category_deltas" in comparison
        assert "promotion_recommendation" in comparison

        # Ensure comparison report was written to disk
        files = os.listdir(str(tmp_path))
        assert any(f.startswith("comparison_") and f.endswith(".json") for f in files)

