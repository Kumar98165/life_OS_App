"""LifeOS - Hardware & GPU Environment Detector.

Detects CUDA availability, active GPU hardware, VRAM capacity, and enforces
strict safety checks to prevent accidental execution on CPU or low-resource
machines (such as the 12GB RAM Intel UHD 620 dev laptop).
"""
import os
import sys
from typing import Dict, Any

# Minimum VRAM required for QLoRA 4-bit fine-tuning of Qwen 2.5:3B (in Gigabytes)
MIN_QLORA_VRAM_GB = 6.0
MIN_LORA_FP16_VRAM_GB = 12.0


class HardwareDetector:
    """Probes runtime hardware capabilities for AI model fine-tuning."""

    @classmethod
    def detect_hardware(cls) -> Dict[str, Any]:
        """Detect CUDA, GPU model, total and available VRAM, and compatibility status."""
        try:
            import torch
            has_torch = True
            cuda_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count() if cuda_available else 0
        except ImportError:
            has_torch = False
            cuda_available = False
            device_count = 0

        info: Dict[str, Any] = {
            "torch_installed": has_torch,
            "cuda_available": cuda_available,
            "device_count": device_count,
            "gpu_name": None,
            "vram_total_gb": 0.0,
            "vram_free_gb": 0.0,
            "is_qlora_compatible": False,
            "is_lora_fp16_compatible": False,
            "warning": None,
        }

        if not cuda_available:
            info["warning"] = (
                "No CUDA GPU detected. Training on CPU or integrated graphics (e.g. Intel UHD 620) "
                "is strictly prohibited due to extreme latency, memory paging risks, and missing quantization kernels."
            )
            return info

        # Inspect Primary GPU
        try:
            import torch
            primary_idx = 0
            gpu_name = torch.cuda.get_device_name(primary_idx)
            total_bytes = torch.cuda.get_device_properties(primary_idx).total_memory
            total_gb = round(total_bytes / (1024 ** 3), 2)

            info["gpu_name"] = gpu_name
            info["vram_total_gb"] = total_gb

            # Free memory calculation
            try:
                free_bytes, _ = torch.cuda.mem_get_info(primary_idx)
                info["vram_free_gb"] = round(free_bytes / (1024 ** 3), 2)
            except Exception:
                info["vram_free_gb"] = total_gb

            info["is_qlora_compatible"] = total_gb >= MIN_QLORA_VRAM_GB
            info["is_lora_fp16_compatible"] = total_gb >= MIN_LORA_FP16_VRAM_GB

            if not info["is_qlora_compatible"]:
                info["warning"] = (
                    f"GPU has {total_gb} GB VRAM, which is below the minimum {MIN_QLORA_VRAM_GB} GB "
                    "required for stable Qwen 2.5:3B QLoRA fine-tuning."
                )
        except Exception as e:
            info["warning"] = f"Failed to probe GPU details: {str(e)}"

        return info

    @classmethod
    def validate_for_training(cls, allow_dry_run: bool = False) -> None:
        """Raise an informative RuntimeError if current hardware cannot safely support training."""
        hw = cls.detect_hardware()

        if allow_dry_run:
            return  # Dry runs only validate config and format data without invoking GPU

        if not hw["cuda_available"]:
            raise RuntimeError(
                f"Hardware validation failed: {hw['warning']}\n"
                "Please run training in an external GPU environment (Google Colab / RunPod / Lambda Cloud) "
                "or run with --dry-run."
            )

        if not hw["is_qlora_compatible"]:
            raise RuntimeError(
                f"Hardware validation failed: {hw['warning']}\n"
                f"Minimum required VRAM for 3B QLoRA is {MIN_QLORA_VRAM_GB} GB."
            )

