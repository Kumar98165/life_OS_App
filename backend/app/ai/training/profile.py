"""LifeOS - Qwen 2.5:3B LoRA & QLoRA Configuration Profile.

Defines hyperparameters, quantization settings, target modules, sequence lengths,
and validation rules for Hugging Face PEFT + TRL fine-tuning.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Target attention & MLP projection modules in Qwen 2.5 architecture
QWEN25_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


class TrainingProfile(BaseModel):
    """Configuration model for Qwen 2.5:3B LoRA / QLoRA fine-tuning."""

    # Model identifiers
    base_model_name: str = "Qwen/Qwen2.5-3B-Instruct"
    base_model_revision: str = "main"

    # Dataset specification
    dataset_version: str = Field(..., description="Step 7 AIDatasetVersion tag")
    dataset_type: str = Field("sft", description="'sft' or 'dpo'")

    # LoRA Parameters
    lora_rank: int = Field(16, ge=4, le=64, description="LoRA attention dimension rank (r)")
    lora_alpha: int = Field(32, ge=8, le=128, description="LoRA alpha scaling parameter")
    lora_dropout: float = Field(0.05, ge=0.0, le=0.5, description="LoRA dropout rate")
    target_modules: List[str] = Field(default_factory=lambda: list(QWEN25_TARGET_MODULES))

    # Quantization (QLoRA)
    use_qlora_4bit: bool = True
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_quant_type: str = "nf4"
    use_nested_quant: bool = True

    # Optimization Hyperparameters
    learning_rate: float = Field(2e-4, ge=1e-6, le=1e-3)
    num_train_epochs: int = Field(3, ge=1, le=10)
    per_device_train_batch_size: int = Field(2, ge=1, le=16)
    gradient_accumulation_steps: int = Field(8, ge=1, le=32)
    gradient_checkpointing: bool = True
    max_seq_length: int = Field(2048, ge=256, le=4096)
    warmup_ratio: float = Field(0.03, ge=0.0, le=0.2)
    weight_decay: float = Field(0.01, ge=0.0, le=0.1)
    lr_scheduler_type: str = "cosine"

    # Reproducibility
    seed: int = 42

    # Logging and Checkpoint Output
    output_dir: str = "./training_artifacts"
    logging_steps: int = 10
    save_strategy: str = "epoch"
    save_total_limit: int = 2

    def to_training_args_dict(self) -> Dict[str, Any]:
        """Convert into a dictionary consumable by transformers.TrainingArguments."""
        return {
            "output_dir": self.output_dir,
            "learning_rate": self.learning_rate,
            "num_train_epochs": self.num_train_epochs,
            "per_device_train_batch_size": self.per_device_train_batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "gradient_checkpointing": self.gradient_checkpointing,
            "warmup_ratio": self.warmup_ratio,
            "weight_decay": self.weight_decay,
            "lr_scheduler_type": self.lr_scheduler_type,
            "logging_steps": self.logging_steps,
            "seed": self.seed,
            "bf16": True,
            "save_strategy": self.save_strategy,
            "save_total_limit": self.save_total_limit,
        }

