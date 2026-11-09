# LifeOS — STEP 9: AI Model Evaluation & Benchmarking Architecture

## 1. Executive Summary

STEP 9 establishes an automated, reproducible model evaluation and benchmarking system for the active `qwen2.5:3b` model and future fine-tuned models (`qwen2.5:3b-lifeos`).

The evaluation system features:
- **Zero Exposure of Private Data**: Built upon curated, synthetic benchmark test cases covering 9 LifeOS capability pillars.
- **Deterministic Metrics**: Evaluates answers based on keyword presence, negative constraint violations, length constraints, and context tokens without relying exclusively on LLM judges.
- **Safety First**: Inference evaluation is strictly decoupled from model training. Production Ollama models are not replaced, nor are fine-tuned candidates promoted automatically.

---

## 2. Evaluation Dataset & 9 Core Pillars

The benchmark suite (`app.ai.evaluation.benchmark.BenchmarkDataset`) defines canonical test cases across 9 operational pillars:

1. **Daily Planning**: Schedule design with focus blocks, breaks, and realistic triage routines.
2. **Task Management**: Prioritization using the Eisenhower Matrix, subtask decomposition.
3. **Goal Setting**: SMART goal conversion, multi-month milestone creation.
4. **Habit Coaching**: Habit loop formation (cue-routine-reward), streak recovery coaching.
5. **Productivity Assistance**: Technique structuring (e.g., Pomodoro timing intervals).
6. **Instruction Following**: Negative constraints ("must not contain"), strict formatting constraints.
7. **Context Understanding**: Reasoning against user profiles and work preferences.
8. **Response Accuracy**: Factual productivity categorization and theory verification.
9. **Personalization**: Tone adaptation, brevity and length boundary adherence.

Every benchmark run computes and records a deterministic **SHA-256 dataset checksum** for auditability and regression tracking.

---

## 3. Deterministic Evaluation Metrics

Implemented in `app.ai.evaluation.metrics.MetricsCalculator`:

- **Answer Relevance**: Ratio of required domain keywords correctly represented in the response.
- **Instruction Following**: Penalty deductions for negative constraints, formatting omissions, or word count overflow.
- **Response Completeness**: Character threshold checks verifying informative depth.
- **Context Utilization**: Matching ratio of user profile/context tokens reflected in the generated guidance.
- **Latency & Throughput**: Milliseconds elapsed (`latency_ms`) and token generation rate (`tokens_per_second`).

---

## 4. Model Comparison Architecture

Implemented in `app.services.model_evaluation_service.ModelEvaluationService`:

- **Active Model Verification**: Evaluates the base model `qwen2.5:3b`.
- **Candidate Handling**: If candidate fine-tuned model (`qwen2.5:3b-lifeos`) has not yet been converted or deployed to Ollama, the engine reports `candidate_unavailable`, saves the base model benchmark report, and continues without errors.
- **Comparative Deltas**: When both models are available, calculates deltas:
  $$\Delta_{\text{score}} = \text{Score}_{\text{cand}} - \text{Score}_{\text{base}}$$
  $$\Delta_{\text{latency}} = \text{Latency}_{\text{cand}} - \text{Latency}_{\text{base}}$$
  $$\Delta_{\text{pass\_rate}} = \text{PassRate}_{\text{cand}} - \text{PassRate}_{\text{base}}$$
- **Promotion Recommendation**:
  - `PASS`: Candidate exhibits higher aggregate quality without regression.
  - `HOLD`: Candidate does not demonstrate demonstrable superiority.
  - *Note*: All recommendations are advisory; human approval is required for deployment.

---

## 5. Execution Instructions

### 5.1 Running the Benchmark Suite
To run the automated model evaluation test suite:
```bash
python -m pytest backend/tests/test_ai_evaluation.py
```

### 5.2 Programmatic Execution
```python
from app.services.model_evaluation_service import ModelEvaluationService

service = ModelEvaluationService()

# Evaluate base model
base_report = service.evaluate_model(model_name="qwen2.5:3b")

# Compare base model against candidate fine-tuned model
comparison = service.compare_models(
    base_model_name="qwen2.5:3b",
    candidate_model_name="qwen2.5:3b-lifeos"
)
```

---

## 6. Verification & Test Evidence

- **AI Evaluation Suite**: `backend/tests/test_ai_evaluation.py` (12 tests, **100% pass rate**).
- **AI Training Pipeline Suite**: `backend/tests/test_ai_training.py` (16 tests, **100% pass rate**).
- **Mobile Unit Test Suite**: `npm --prefix mobile test` (158 tests, **100% pass rate**).
- **Mobile TypeScript Verification**: `npm --prefix mobile run typecheck` (**0 errors**).
