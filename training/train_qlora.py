"""LifeOS - Standalone SFT Trainer for Google Colab / External GPU.

Reads exported LifeOS JSONL dataset, validates SHA-256 manifest hash,
configures Qwen 2.5:3B with 4-bit NF4 bitsandbytes quantization,
trains LoRA adapter weights with Hugging Face TRL SFTTrainer,
and saves verifiable artifacts with cryptographic digests.
"""
import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

# Target modules for Qwen 2.5 attention and MLP projections
QWEN25_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


def compute_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def compute_directory_checksum(dir_path: str) -> str:
    hasher = hashlib.sha256()
    for root, _, files in sorted(os.walk(dir_path)):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            hasher.update(fname.encode("utf-8"))
            with open(fpath, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
    return hasher.hexdigest()


def format_chatml_record(record: dict) -> dict:
    """Format LifeOS training sample into ChatML conversation turns."""
    messages = []
    system_prompt = (
        "You are LifeOS, an intelligent, empathetic, and highly disciplined personal operating system assistant. "
        "Your objective is to provide structured, actionable, and context-aware assistance for tasks, planner blocks, habits, and personal goals."
    )
    if "context" in record and record["context"]:
        system_prompt += f"\n\nUser Context:\n{record['context']}"

    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": record.get("prompt", record.get("prompt_input", ""))})
    messages.append({"role": "assistant", "content": record.get("response", record.get("chosen_response", ""))})
    return {"messages": messages}


def run_training(
    dataset_path: str,
    output_dir: str = "./training_artifacts/qwen25_3b_lifeos",
    base_model_name: str = "Qwen/Qwen2.5-3B-Instruct",
    lora_rank: int = 16,
    lora_alpha: int = 32,
    learning_rate: float = 2e-4,
    epochs: int = 1,
    batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    max_seq_length: int = 1024,
    val_split_ratio: float = 0.2,
    seed: int = 42,
) -> dict:
    print("\n" + "=" * 60)
    print(" LIFEOS AI - QWEN 2.5:3B QLORA TRAINING RUNNER")
    print("=" * 60)

    # 1. Verify Dataset
    if not os.path.isfile(dataset_path):
        raise FileNotFoundError(f"Training dataset not found at: {dataset_path}")

    dataset_hash = compute_sha256(dataset_path)
    print(f"[*] Dataset File      : {dataset_path}")
    print(f"[*] Dataset SHA-256   : {dataset_hash}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError("Dataset file contains zero records.")

    raw_records = [json.loads(line) for line in lines]
    total_samples = len(raw_records)
    print(f"[*] Total Samples     : {total_samples}")

    if total_samples < 5:
        raise ValueError(f"Insufficient samples ({total_samples}). Minimum technical floor is 5.")

    formatted_dataset = [format_chatml_record(r) for r in raw_records]

    # Split train and validation deterministically
    import random
    random.seed(seed)
    indices = list(range(total_samples))
    random.shuffle(indices)

    val_count = max(1, int(total_samples * val_split_ratio))
    val_indices = set(indices[:val_count])
    train_records = [formatted_dataset[i] for i in range(total_samples) if i not in val_indices]
    val_records = [formatted_dataset[i] for i in range(total_samples) if i in val_indices]

    print(f"[*] Train Samples     : {len(train_records)}")
    print(f"[*] Validation Samples: {len(val_records)}")

    # 2. Imports inside runner so local dev environment is never polluted
    import torch
    from datasets import Dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer

    train_data = Dataset.from_list(train_records)
    val_data = Dataset.from_list(val_records)

    # 3. Quantization Configuration (4-bit NF4)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"[*] Loading Base Model: {base_model_name} (4-bit NF4)...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    # 4. LoRA Configuration
    peft_config = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=QWEN25_TARGET_MODULES,
    )
    model = get_peft_model(model, peft_config)
    trainable_params, all_params = model.get_nb_trainable_parameters()
    print(f"[*] Trainable Parameters: {trainable_params:,} / {all_params:,} ({100 * trainable_params / all_params:.3f}%)")

    # 5. Training Arguments
    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_output_dir = os.path.join(output_dir, f"run_{run_timestamp}")
    os.makedirs(run_output_dir, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=run_output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.03,
        logging_steps=1,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        max_grad_norm=0.3,
        seed=seed,
        report_to="none",
    )

    # 6. SFT Trainer
    def formatting_prompts_func(example):
        return tokenizer.apply_chat_template(
            example["messages"],
            tokenize=False,
            add_generation_prompt=False
        )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_data,
        eval_dataset=val_data,
        peft_config=peft_config,
        formatting_func=formatting_prompts_func,
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
    )

    print("\n[*] Starting Fine-Tuning Execution...")
    start_time = time.time()
    train_result = trainer.train()
    training_duration_sec = round(time.time() - start_time, 2)
    print(f"[+] Training completed in {training_duration_sec} seconds.")

    # 7. Evaluate and Save Artifacts
    eval_metrics = trainer.evaluate()
    final_adapter_dir = os.path.join(run_output_dir, "adapter")
    trainer.save_model(final_adapter_dir)
    tokenizer.save_pretrained(final_adapter_dir)

    adapter_checksum = compute_directory_checksum(final_adapter_dir)
    print(f"[+] Adapter saved to : {final_adapter_dir}")
    print(f"[+] Adapter Checksum: {adapter_checksum}")

    # 8. Compile Manifest
    manifest = {
        "run_id": f"run_{run_timestamp}",
        "base_model": base_model_name,
        "dataset_path": dataset_path,
        "dataset_hash": dataset_hash,
        "sample_count_total": total_samples,
        "sample_count_train": len(train_records),
        "sample_count_val": len(val_records),
        "hyperparameters": {
            "lora_rank": lora_rank,
            "lora_alpha": lora_alpha,
            "learning_rate": learning_rate,
            "epochs": epochs,
            "batch_size": batch_size,
            "gradient_accumulation_steps": gradient_accumulation_steps,
            "max_seq_length": max_seq_length,
            "seed": seed,
        },
        "metrics": {
            "train_loss": train_result.training_loss,
            "val_loss": eval_metrics.get("eval_loss"),
            "training_duration_sec": training_duration_sec,
            "optimizer_steps": train_result.global_step,
        },
        "adapter_directory": final_adapter_dir,
        "adapter_checksum": adapter_checksum,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    manifest_path = os.path.join(run_output_dir, "training_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Run manifest saved: {manifest_path}")
    print("=" * 60 + "\n")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_qlora.py <path_to_dataset.jsonl>")
        sys.exit(1)
    run_training(dataset_path=sys.argv[1])
