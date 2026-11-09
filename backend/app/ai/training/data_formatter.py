"""LifeOS - Qwen 2.5 Training Dataset Formatter (SFT & DPO).

Transforms approved, sanitized Step 7 dataset records into canonical
Qwen 2.5 chat instruction formats.
"""
from typing import Dict, Any, List, Optional
import json

SYSTEM_PROMPT_DEFAULT = (
    "You are LifeOS, an intelligent, empathetic, and highly disciplined personal operating system assistant. "
    "Your objective is to provide structured, actionable, and context-aware assistance for tasks, planner blocks, "
    "habits, and personal goals."
)


class TrainingDataFormatter:
    """Formats and validates records into HuggingFace/TRL compatible SFT and DPO formats."""

    @classmethod
    def format_sft_turn(cls, prompt: str, completion: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Convert prompt & completion into Qwen 2.5 messages format for TRL SFTTrainer.

        Format:
        {
            "messages": [
                {"role": "system", "content": ...},
                {"role": "user", "content": ...},
                {"role": "assistant", "content": ...}
            ]
        }
        """
        sys_content = (system_prompt or SYSTEM_PROMPT_DEFAULT).strip()
        user_content = prompt.strip()
        assistant_content = completion.strip()

        if not user_content:
            raise ValueError("Prompt cannot be empty.")
        if not assistant_content:
            raise ValueError("Completion cannot be empty.")

        return {
            "messages": [
                {"role": "system", "content": sys_content},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ]
        }

    @classmethod
    def format_dpo_pair(
        cls,
        prompt: str,
        chosen: str,
        rejected: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert prompt, chosen, and rejected completions into DPOTrainer format.

        Format:
        {
            "prompt": "...",
            "chosen": "...",
            "rejected": "..."
        }
        """
        sys_content = (system_prompt or SYSTEM_PROMPT_DEFAULT).strip()
        user_content = prompt.strip()
        chosen_content = chosen.strip()
        rejected_content = rejected.strip() if rejected else ""

        if not user_content:
            raise ValueError("Prompt cannot be empty.")
        if not chosen_content:
            raise ValueError("Chosen completion cannot be empty.")
        if not rejected_content:
            raise ValueError("Rejected completion cannot be empty for DPO preference tuning.")
        if chosen_content.lower() == rejected_content.lower():
            raise ValueError("Chosen and rejected completions cannot be identical.")

        # Full prompt includes system prompt context
        formatted_prompt = f"<|im_start|>system\n{sys_content}<|im_end|>\n<|im_start|>user\n{user_content}<|im_end|>\n<|im_start|>assistant\n"

        return {
            "prompt": formatted_prompt,
            "chosen": chosen_content + "<|im_end|>",
            "rejected": rejected_content + "<|im_end|>"
        }

    @classmethod
    def prepare_dataset_from_records(
        cls,
        records: List[Dict[str, Any]],
        dataset_type: str = "sft",
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Validate, filter, and format a batch of exported Step 7 records."""
        formatted_batch = []
        errors = []

        for idx, rec in enumerate(records):
            prompt = rec.get("prompt")
            completion = rec.get("completion")
            rejected = rec.get("rejected_completion")

            try:
                if dataset_type == "dpo":
                    if not rejected:
                        continue  # Skip records without preference pairs for DPO
                    formatted_batch.append(
                        cls.format_dpo_pair(prompt, completion, rejected, system_prompt)
                    )
                else:
                    # SFT default
                    if not completion:
                        continue
                    formatted_batch.append(
                        cls.format_sft_turn(prompt, completion, system_prompt)
                    )
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        return formatted_batch

