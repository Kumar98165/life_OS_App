"""LifeOS - Ollama Model Converter and Packaging Specification.

Coordinates:
- Merging PEFT LoRA adapter weights with base Qwen 2.5:3B model
- GGUF export conversion instructions (via llama.cpp convert_hf_to_gguf.py)
- Modelfile generation for local Ollama testing and deployment
- Preserving existing production inference settings intact
"""
import os
import json
from typing import Dict, Any, Optional

MODELFILE_TEMPLATE = """# LifeOS Fine-Tuned Qwen 2.5:3B Modelfile
FROM {gguf_model_path}

# Set context window and temperature
PARAMETER num_ctx 4096
PARAMETER temperature 0.7
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"

# Set LifeOS system prompt
SYSTEM \"\"\"You are LifeOS, an intelligent, empathetic, and highly disciplined personal operating system assistant. Your objective is to provide structured, actionable, and context-aware assistance for tasks, planner blocks, habits, and personal goals.\"\"\"
"""


class OllamaExporter:
    """Manages adapter packaging, Modelfile generation, and GGUF conversion specs."""

    @classmethod
    def generate_modelfile(
        cls,
        gguf_model_path: str,
        output_dir: str,
        model_name: str = "qwen2.5:3b-lifeos"
    ) -> str:
        """Create a standard Ollama Modelfile for packaging the fine-tuned model.

        Returns path to the written Modelfile.
        """
        os.makedirs(output_dir, exist_ok=True)
        modelfile_path = os.path.join(output_dir, "Modelfile")

        content = MODELFILE_TEMPLATE.format(gguf_model_path=gguf_model_path)
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(content)

        return modelfile_path

    @classmethod
    def get_packaging_instructions(
        cls,
        adapter_dir: str,
        output_dir: str,
        model_tag: str = "qwen2.5:3b-lifeos"
    ) -> Dict[str, Any]:
        """Generate verifiable command sequence for external conversion and Ollama import."""
        return {
            "model_tag": model_tag,
            "adapter_dir": adapter_dir,
            "output_dir": output_dir,
            "steps": [
                {
                    "step": 1,
                    "action": "Merge LoRA adapter into base model",
                    "command": (
                        f"python -m app.ai.training.scripts.merge_lora "
                        f"--base_model Qwen/Qwen2.5-3B-Instruct "
                        f"--adapter_dir {adapter_dir} "
                        f"--output_dir {output_dir}/merged_hf"
                    )
                },
                {
                    "step": 2,
                    "action": "Convert merged Hugging Face model to GGUF format",
                    "command": (
                        f"python convert_hf_to_gguf.py {output_dir}/merged_hf "
                        f"--outtype q4_k_m "
                        f"--outfile {output_dir}/{model_tag}-q4_k_m.gguf"
                    )
                },
                {
                    "step": 3,
                    "action": "Create and register model in Ollama",
                    "command": f"ollama create {model_tag} -f {output_dir}/Modelfile"
                },
                {
                    "step": 4,
                    "action": "Verify local inference without altering default production model",
                    "command": f"ollama run {model_tag} \"What are my top productivity rules?\""
                }
            ],
            "safety_note": (
                "Do NOT replace the active production Ollama model 'qwen2.5:3b' until benchmark evaluation "
                "and explicit sign-off are completed."
            )
        }

