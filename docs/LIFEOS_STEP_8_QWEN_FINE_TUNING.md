# LifeOS — STEP 8: Qwen 2.5:3B Fine-Tuning Pipeline (LoRA / QLoRA) Specification & Run Guide

## 1. Executive Summary

STEP 8 establishes a reproducible, decoupled fine-tuning pipeline for **Qwen 2.5:3B Instruct** tailored to LifeOS domain tasks (task prioritization, habit coaching, schedule optimization, and structured personal assistance).

The pipeline strictly consumes verified, immutable **STEP 7** dataset version snapshots (`.jsonl`) accompanied by their SHA-256 manifest and export checksums.

---

## 2. Hardware Architecture & Safety Verification

### 2.1 Hardware Guardrails
- **Dev Machine Context**: Intel Core i3 / Intel UHD 620 / 12 GB RAM / Windows.
- **Strict Prohibition**: PyTorch/bitsandbytes GPU training is **strictly prevented** on the development laptop to prevent memory thrashing, CPU system lockups, or invalid CUDA execution.
- **Fail-Safe Gate**: `HardwareDetector.validate_for_training(allow_dry_run=False)` checks CUDA availability and VRAM capacity (minimum 6.0 GB for QLoRA 4-bit; 12.0 GB for LoRA FP16). If run on unsupported hardware without `--dry-run`, execution halts safely with a descriptive `RuntimeError`.
- **Dry-Run Engine**: Allows full pipeline execution on local machines, validating dataset integrity, ChatML tokenization format, target modules, and hyperparameter profiles without requiring PyTorch or CUDA.

---

## 3. Training Formats (SFT & DPO)

### 3.1 SFT (Supervised Fine-Tuning) — Canonical Qwen 2.5 ChatML
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are LifeOS, an intelligent, empathetic, and highly disciplined personal operating system assistant..."
    },
    {
      "role": "user",
      "content": "Help me prioritize my morning tasks"
    },
    {
      "role": "assistant",
      "content": "Here is your prioritized morning schedule: 1. Deep work 2. Email triage"
    }
  ]
}
```

### 3.2 DPO (Direct Preference Optimization) — TRL Chat Template
```json
{
  "prompt": "<|im_start|>system\nYou are LifeOS...<|im_end|>\n<|im_start|>user\nHelp me prioritize my morning tasks<|im_end|>\n<|im_start|>assistant\n",
  "chosen": "Here is your prioritized morning schedule: 1. Deep work 2. Email triage<|im_end|>",
  "rejected": "Just do whatever you feel like doing.<|im_end|>"
}
```

---

## 4. LoRA / QLoRA Hyperparameter Profile

Implemented in `app.ai.training.profile.TrainingProfile`:
- **Base Model**: `Qwen/Qwen2.5-3B-Instruct`
- **LoRA Rank ($r$)**: `16`
- **LoRA Alpha ($\alpha$)**: `32` (Scaling factor $\frac{\alpha}{r} = 2.0$)
- **LoRA Dropout**: `0.05`
- **Target Modules**: `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` (All attention projections + MLP feedforward layers)
- **Quantization (QLoRA 4-bit)**:
  - `load_in_4bit`: `True`
  - `bnb_4bit_quant_type`: `"nf4"`
  - `bnb_4bit_compute_dtype`: `"bfloat16"`
  - `bnb_4bit_use_double_quant`: `True`
- **Optimizer & Scheduler**:
  - `learning_rate`: `2e-4`
  - `lr_scheduler_type`: `"cosine"`
  - `warmup_ratio`: `0.03`
  - `weight_decay`: `0.01`
  - `max_seq_length`: `2048`
  - `gradient_checkpointing`: `True`
  - `seed`: `42` (Deterministic reproducibility)

---

## 5. Ollama Packaging & Conversion

Fine-tuned models are packaged under an isolated tag (e.g., `qwen2.5:3b-lifeos`) to protect active production inference (`qwen2.5:3b` in Ollama).

### 5.1 Generated `Modelfile`
```dockerfile
# LifeOS Fine-Tuned Qwen 2.5:3B Modelfile
FROM output/gguf/qwen2.5-3b-lifeos-q4_k_m.gguf

PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"

SYSTEM """You are LifeOS, an intelligent, empathetic, and highly disciplined personal operating system assistant. Your objective is to provide structured, actionable, and context-aware assistance for tasks, planner blocks, habits, and personal goals."""
```

### 5.2 Step-by-Step Packaging Pipeline
1. **Merge Adapter**:
   ```bash
   python -m app.ai.training.scripts.merge_lora \
     --base_model Qwen/Qwen2.5-3B-Instruct \
     --adapter_dir ./training_artifacts/run_v1.0.0_xxx/adapter \
     --output_dir ./training_artifacts/merged_hf
   ```
2. **Convert to GGUF**:
   ```bash
   python llama.cpp/convert_hf_to_gguf.py ./training_artifacts/merged_hf \
     --outtype q4_k_m \
     --outfile ./training_artifacts/qwen2.5-3b-lifeos-q4_k_m.gguf
   ```
3. **Register in Local Ollama**:
   ```bash
   ollama create qwen2.5:3b-lifeos -f ./training_artifacts/Modelfile
   ```
4. **Smoke Test Before Deployment**:
   ```bash
   ollama run qwen2.5:3b-lifeos "What are my daily focus blocks?"
   ```

---

## 6. Verification & Test Evidence

- **New Test Suite**: `backend/tests/test_ai_training.py` (16 unit tests, **100% pass rate**).
- **STEP 7 Regression**: `backend/tests/test_ai_dataset.py` (8 tests, **100% pass rate**).
- **Mobile Regression**: `npm --prefix mobile test` (158 tests across 11 suites, **100% pass rate**).
- **Mobile TypeScript**: `npm --prefix mobile run typecheck` (**0 errors**).
