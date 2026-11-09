# LifeOS AI — External GPU Training Guide

This guide details how to execute **actual QLoRA 4-bit fine-tuning** of `Qwen/Qwen2.5-3B-Instruct` for LifeOS without running compute on the local development laptop or paying for cloud GPU instances.

---

## 1. Hardware & Environment Architecture

- **Active Production Model**: `qwen2.5:3b` in local Ollama (untouched and protected).
- **Development Workstation**: Intel UHD 620 / 12GB RAM (CPU only; training strictly prohibited).
- **Target Training Environment**: Google Colab Free Tier (Nvidia T4 GPU / 15.3 GB VRAM).

---

## 2. Step-by-Step Training Execution Workflow

### Step 1: Export LifeOS Dataset
In LifeOS backend, generate an immutable dataset version snapshot via `/api/v1/ai/dataset/versions` and export the verified JSONL:
```bash
# Output file contains sanitized, consent-approved ChatML records
lifeos_training_dataset.jsonl
```

### Step 2: Open Colab Notebook
1. Navigate to Google Colab: https://colab.research.google.com
2. Upload `training/notebooks/LIFEOS_QWEN25_3B_QLORA.ipynb`.
3. Set runtime to GPU: **Runtime -> Change runtime type -> T4 GPU**.

### Step 3: Run Training Cells
1. **Cell 1**: Hardware pre-flight verification (verifies CUDA, T4 GPU, 15GB VRAM, and disk space).
2. **Cell 2**: Pinned dependency installation (`torch==2.2.2`, `transformers==4.40.2`, `peft==0.10.0`, `trl==0.8.6`, `bitsandbytes==0.43.1`).
3. **Cell 3**: Upload `lifeos_training_dataset.jsonl`. Computes and prints dataset SHA-256.
4. **Cell 4**: SFTTrainer execution. Loads Qwen 2.5:3B NF4 quantized, injects LoRA rank 16 target modules, runs 1 epoch, and outputs real train loss and val loss.
5. **Cell 5**: Artifact packaging and SHA-256 calculation. Generates `training_manifest.json` and zips adapter files (`lifeos_qwen25_3b_adapter.zip`).

### Step 4: Import Trained Adapter into LifeOS
1. Download `lifeos_qwen25_3b_adapter.zip` from Colab.
2. Unzip into `training_artifacts/` directory in LifeOS workspace.
3. Record real training completion in LifeOS:
   ```http
   POST /api/v1/ai/improvement/jobs/<job_id>/record-completion
   {
     "artifact_checksum": "<sha256_from_manifest>",
     "artifact_directory": "./training_artifacts/<run_id>/adapter",
     "metrics": {
       "train_loss": 0.42,
       "val_loss": 0.38
     }
   }
   ```
4. Run candidate benchmark evaluation via Step 9 / Step 11 (`POST /jobs/<job_id>/post-train`).
5. Only after administrator approval, activate model under separate tag `qwen2.5:3b-lifeos-v1`.
