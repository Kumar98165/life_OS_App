"""LifeOS - Deterministic AI Evaluation Metrics Calculator (Step 9).

Calculates deterministic evaluation scores without relying exclusively on LLM judges:
- Answer Relevance (keyword & semantic focus)
- Instruction Following (structure constraints, negative constraints)
- Response Completeness (character & element requirements)
- Factual Consistency (factual keyword presence & non-contradiction)
- Context Utilization (grounding against provided context)
- Latency & Token Generation Throughput (tokens/sec)
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class EvaluationMetricResult(BaseModel):
    """Result of an individual metric evaluation."""
    metric_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    passed: bool
    reasoning: str
    details: Dict[str, Any] = Field(default_factory=dict)


class EvaluatedCaseResult(BaseModel):
    """Comprehensive evaluation result for a single benchmark test case."""
    test_id: str
    category: str
    prompt: str
    context: Optional[str] = None
    response_text: str
    latency_ms: float
    token_count: int
    tokens_per_sec: float
    is_success: bool
    error: Optional[str] = None
    metrics: Dict[str, EvaluationMetricResult]
    overall_score: float = Field(..., ge=0.0, le=1.0)


class MetricsCalculator:
    """Calculates deterministic scores for benchmark responses."""

    @classmethod
    def calculate_answer_relevance(
        cls,
        response_text: str,
        expected_keywords: List[str]
    ) -> EvaluationMetricResult:
        """Measure match ratio of expected domain keywords in the response."""
        if not response_text or not response_text.strip():
            return EvaluationMetricResult(
                metric_name="answer_relevance",
                score=0.0,
                passed=False,
                reasoning="Response was empty or blank.",
                details={"matched": [], "total_expected": len(expected_keywords)}
            )

        resp_lower = response_text.lower()
        matched = [kw for kw in expected_keywords if kw.lower() in resp_lower]
        score = round(len(matched) / max(len(expected_keywords), 1), 2)
        passed = score >= 0.5

        return EvaluationMetricResult(
            metric_name="answer_relevance",
            score=score,
            passed=passed,
            reasoning=f"Matched {len(matched)} of {len(expected_keywords)} expected domain keywords.",
            details={"matched": matched, "total_expected": len(expected_keywords)}
        )

    @classmethod
    def calculate_instruction_following(
        cls,
        response_text: str,
        benchmark_item: Dict[str, Any]
    ) -> EvaluationMetricResult:
        """Evaluate structural formatting, negative constraints, and length constraints."""
        if not response_text:
            return EvaluationMetricResult(
                metric_name="instruction_following",
                score=0.0,
                passed=False,
                reasoning="Empty response violated all instructions."
            )

        resp_lower = response_text.lower()
        score_deductions = 0.0
        reasons = []

        # 1. Negative constraints check (must_not_contain)
        must_not = benchmark_item.get("must_not_contain", [])
        violated_forbidden = [term for term in must_not if term.lower() in resp_lower]
        if violated_forbidden:
            score_deductions += 0.35 * len(violated_forbidden)
            reasons.append(f"Violated negative constraints: {violated_forbidden}")

        # 2. Maximum words constraint (e.g. for concise responses)
        max_words = benchmark_item.get("max_words")
        words = response_text.strip().split()
        if max_words and len(words) > max_words:
            excess = len(words) - max_words
            score_deductions += min(0.4, 0.05 * excess)
            reasons.append(f"Exceeded word limit ({len(words)} > {max_words})")

        # 3. Structural checks
        required_structure = benchmark_item.get("required_structure")
        if required_structure in ("numbered_list", "strict_numbered_list"):
            has_list = bool(re.search(r"1[\.\)]\s+", response_text))
            if not has_list:
                score_deductions += 0.4
                reasons.append("Missing required numbered list format.")

        final_score = max(0.0, round(1.0 - score_deductions, 2))
        passed = final_score >= 0.65

        reasoning = "; ".join(reasons) if reasons else "Fully followed all structural and negative constraints."

        return EvaluationMetricResult(
            metric_name="instruction_following",
            score=final_score,
            passed=passed,
            reasoning=reasoning,
            details={"reasons": reasons}
        )

    @classmethod
    def calculate_response_completeness(
        cls,
        response_text: str,
        min_length_chars: int
    ) -> EvaluationMetricResult:
        """Evaluate if response satisfies minimum informative length without truncation."""
        char_len = len(response_text.strip()) if response_text else 0
        if char_len >= min_length_chars:
            return EvaluationMetricResult(
                metric_name="response_completeness",
                score=1.0,
                passed=True,
                reasoning=f"Response length ({char_len} chars) meets minimum requirement ({min_length_chars} chars).",
                details={"actual_chars": char_len, "min_required": min_length_chars}
            )

        ratio = round(char_len / max(min_length_chars, 1), 2)
        return EvaluationMetricResult(
            metric_name="response_completeness",
            score=ratio,
            passed=ratio >= 0.7,
            reasoning=f"Response is too brief ({char_len} chars vs {min_length_chars} min required).",
            details={"actual_chars": char_len, "min_required": min_length_chars}
        )

    @classmethod
    def calculate_context_utilization(
        cls,
        response_text: str,
        context: Optional[str]
    ) -> EvaluationMetricResult:
        """Check whether context clues were incorporated into the answer."""
        if not context:
            # If no context was provided, default to full score (not applicable)
            return EvaluationMetricResult(
                metric_name="context_utilization",
                score=1.0,
                passed=True,
                reasoning="No context required for this case; context utilization passed by default.",
                details={"context_present": False}
            )

        # Extract meaningful alphanumeric terms from context (>3 chars)
        context_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", context.lower()))
        resp_lower = response_text.lower()
        matched_context = [w for w in context_words if w in resp_lower]

        ratio = round(len(matched_context) / max(len(context_words), 1), 2)
        passed = ratio >= 0.25

        return EvaluationMetricResult(
            metric_name="context_utilization",
            score=min(1.0, ratio * 2),  # Scale 50% overlap to 1.0
            passed=passed,
            reasoning=f"Referenced {len(matched_context)} key contextual tokens from provided profile.",
            details={"matched_tokens": matched_context[:5]}
        )

