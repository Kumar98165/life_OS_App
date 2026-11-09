# LifeOS — STEP 9: AI Model Evaluation & Benchmarking Architecture

## 1. Executive Summary

STEP 9 establishes an automated, reproducible model evaluation and benchmarking system for the active `qwen2.5:3b` model and future fine-tuned models (`qwen2.5:3b-lifeos`).

The evaluation system features:
- **Zero Exposure of Private Data**: Built upon curated, synthetic benchmark test cases covering 9 LifeOS capability pillars.
- **Deterministic Metrics**: Evaluates answers based on keyword coverage, negative constraint violations, length constraints, and context tokens without relying exclusively on LLM judges.
- **Safety First**: Inference evaluation is strictly decoupled from model training. Production Ollama models are not replaced, nor are fine-tuned candidates promoted automatically.

---

## 2. Actual Live Benchmark Results (`qwen2.5:3b`)

Executed live against local Ollama running on the development workstation (`Intel Core i3 / 12 GB RAM / CPU inference`):

- **Model Identifier**: `qwen2.5:3b`
- **Benchmark Version**: `v1.0.0-lifeos-bench`
- **Benchmark Checksum (SHA-256)**: `f0ed8d846db017c5ef40160f49ea49c6955418312ce486e207781b12fc526761`
- **Timestamp**: `2026-11-09T12:43:36.876236+00:00` to `2026-11-09T12:51:43.942566+00:00`
- **Total Execution Duration**: `487.06s (~8.1 minutes)`
- **Total Benchmark Cases**: `13`
- **Passed Cases**: `9 (69.2%)`
- **Failed Cases**: `4 (30.8%)`
- **Overall Aggregate Score**: `0.785 / 1.0`
- **Average Response Latency**: `37,305.39 ms (~37.3s)`
- **Token Generation Throughput**: `4.62 tokens/sec` (measured on local CPU)

### 2.1 Category Breakdown
| Category | Cases | Average Score | Pass Rate | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Task Management** | 2 | **1.00** | 100% | Full Pass |
| **Productivity Assistance** | 1 | **1.00** | 100% | Full Pass |
| **Instruction Following** | 1 | **1.00** | 100% | Full Pass |
| **Context Understanding** | 1 | **1.00** | 100% | Full Pass |
| **Goal Setting** | 2 | **0.93** | 100% | Pass |
| **Response Accuracy** | 1 | **0.88** | 100% | Pass |
| **Habit Coaching** | 2 | **0.57** | 50% | Partial Pass |
| **Personalization** | 1 | **0.57** | 0% | Sub-threshold |
| **Daily Planning** | 2 | **0.38** | 0% | Timeout & Keyword Gap |

### 2.2 Live Failure Analysis
1. `bench-plan-001` (Daily Planning): Timed out after 60s during local CPU inference on a complex schedule prompt.
2. `bench-habit-002` (Habit Coaching): Timed out after 60s during local CPU inference.
3. `bench-plan-002` (Daily Planning): Score `0.60` (threshold `0.65`). Model omitted explicit `1. 2. 3.` formatting.
4. `bench-pers-001` (Personalization): Score `0.57` (threshold `0.65`). Model gave an ultra-concise answer ("Snack on almonds or have a small protein bar"), satisfying brevity but missing contextual profile token echoes.

---

## 3. Evaluation Dataset & 9 Core Pillars

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

## 4. Deterministic Evaluation Metrics & Limitations

Implemented in `app.ai.evaluation.metrics.MetricsCalculator`:

- **Answer Relevance**: Ratio of required domain keywords correctly represented in the response.
- **Instruction Following**: Penalty deductions for negative constraints, formatting omissions, or word count overflow.
- **Response Completeness**: Character threshold checks verifying informative depth.
- **Context Utilization**: Matching ratio of user profile/context tokens reflected in the generated guidance.
- **Latency & Throughput**: Milliseconds elapsed (`latency_ms`) and token generation rate (`tokens_per_second`).

### 4.1 Metric Distinctions & Known Limitations
> [!IMPORTANT]
> **Deterministic Proxies vs. Factual Ground Truth**:
> - Keyword matching serves as an efficient, deterministic proxy for domain alignment, but **does not prove semantic or factual correctness**. A response containing keywords can still convey flawed advice.
> - Context utilization measures lexical token overlap with the user profile, but does not guarantee nuanced contextual reasoning.
> - Hardware latency and throughput on CPU (Intel UHD 620 / Core i3) vary with background system load and cannot substitute for dedicated cloud GPU benchmark telemetry.

---

## 5. Model Comparison Architecture

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

## 6. Verification & Test Evidence

- **AI Evaluation Suite**: `backend/tests/test_ai_evaluation.py` (12 tests, **100% pass rate**).
- **AI Training Pipeline Suite**: `backend/tests/test_ai_training.py` (16 tests, **100% pass rate**).
- **STEP 7 Dataset Management Suite**: `backend/tests/test_ai_dataset.py` (8 tests, **100% pass rate**).
- **Full AI Regression**: 36 passed in 14.27s.
- **Mobile Unit Test Suite**: `npm --prefix mobile test` (158 tests, **100% pass rate**).
- **Mobile TypeScript Verification**: `npm --prefix mobile run typecheck` (**0 errors**).
