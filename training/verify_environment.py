"""LifeOS - Standalone Hardware Verification Utility for External Training Environments.

Checks CUDA availability, GPU device name, VRAM headroom, and PyTorch compatibility.
Halts execution safely if hardware requirements are not satisfied.
"""
import sys
import shutil

MIN_QLORA_VRAM_GB = 6.0
RECOMMENDED_VRAM_GB = 12.0


def verify_hardware_environment() -> dict:
    print("=" * 60)
    print(" LIFEOS AI - GPU ENVIRONMENT PRE-FLIGHT VERIFICATION")
    print("=" * 60)

    try:
        import torch
    except ImportError:
        print("[FATAL ERROR] PyTorch is not installed.")
        print("Please install requirements using: pip install -r requirements-colab.txt")
        sys.exit(1)

    cuda_available = torch.cuda.is_available()
    print(f"[*] PyTorch Version: {torch.__version__}")
    print(f"[*] CUDA Available : {cuda_available}")

    if not cuda_available:
        print("\n[STOPPED] No CUDA-capable GPU detected.")
        print("LifeOS Qwen 2.5:3B QLoRA fine-tuning cannot run on CPU.")
        print("Action Required: In Google Colab, select Runtime -> Change runtime type -> T4 GPU.")
        sys.exit(1)

    device_count = torch.cuda.device_count()
    device_name = torch.cuda.get_device_name(0)
    total_vram_bytes = torch.cuda.get_device_properties(0).total_memory
    total_vram_gb = round(total_vram_bytes / (1024 ** 3), 2)

    try:
        free_vram_bytes, _ = torch.cuda.mem_get_info(0)
        free_vram_gb = round(free_vram_bytes / (1024 ** 3), 2)
    except Exception:
        free_vram_gb = total_vram_gb

    print(f"[*] Active GPU       : {device_name} (Device count: {device_count})")
    print(f"[*] Total VRAM       : {total_vram_gb} GB")
    print(f"[*] Free VRAM        : {free_vram_gb} GB")

    # Check disk space
    disk = shutil.disk_usage(".")
    free_disk_gb = round(disk.free / (1024 ** 3), 2)
    print(f"[*] Free Disk Space  : {free_disk_gb} GB")

    if total_vram_gb < MIN_QLORA_VRAM_GB:
        print(f"\n[INSUFFICIENT HARDWARE] Detected {total_vram_gb} GB VRAM.")
        print(f"Minimum required VRAM for Qwen 2.5:3B QLoRA is {MIN_QLORA_VRAM_GB} GB.")
        sys.exit(1)

    if free_disk_gb < 10.0:
        print(f"\n[WARNING] Low disk space ({free_disk_gb} GB free). Base model weights require ~7 GB.")

    print("\n[VERIFICATION PASSED] Hardware satisfies QLoRA fine-tuning prerequisites.")
    print("=" * 60)
    return {
        "device_name": device_name,
        "total_vram_gb": total_vram_gb,
        "free_vram_gb": free_vram_gb,
        "free_disk_gb": free_disk_gb,
    }


if __name__ == "__main__":
    verify_hardware_environment()
