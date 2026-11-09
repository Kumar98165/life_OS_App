"""Unit tests for LifeOS STEP 8 - Qwen 2.5:3B LoRA / QLoRA Fine-Tuning Pipeline."""

import os
import pytest
from pydantic import ValidationError

from app.ai.training.hardware import HardwareDetector
from app.ai.training.data_formatter import TrainingDataFormatter
from app.ai.training.profile import TrainingProfile
from app.ai.training.runner import TrainingPipelineRunner
from app.ai.training.ollama_export import OllamaExporter, MODELFILE_TEMPLATE


class TestHardwareDetector:
    """Tests for hardware detection and training safety gates."""

    def test_detect_hardware_returns_valid_spec(self):
        spec = HardwareDetector.detect_hardware()
        assert isinstance(spec, dict)
        assert "cuda_available" in spec
        assert isinstance(spec["cuda_available"], bool)
        assert "device_count" in spec
        assert "vram_total_gb" in spec
        assert "vram_free_gb" in spec
        assert "is_qlora_compatible" in spec

    def test_allow_dry_run_bypasses_gpu_check(self):
        # Even without a supported GPU, dry-run should never raise
        HardwareDetector.validate_for_training(allow_dry_run=True)

    def test_insufficient_hardware_raises_runtime_error_when_dry_run_false(self):
        # If running on CPU or low-end GPU, validate_for_training must raise a descriptive RuntimeError
        spec = HardwareDetector.detect_hardware()
        if not spec["cuda_available"] or not spec["is_qlora_compatible"]:
            with pytest.raises(RuntimeError) as exc_info:
                HardwareDetector.validate_for_training(allow_dry_run=False)
            assert "hardware validation failed" in str(exc_info.value).lower()


class TestDataFormatter:
    """Tests for SFT and DPO chat template formatting."""

    def test_format_sft_turn_chatml(self):
        system_prompt = "You are LifeOS assistant."
        user_prompt = "Schedule a workout."
        completion = "I've scheduled your workout for 7 AM."

        sft = TrainingDataFormatter.format_sft_turn(
            prompt=user_prompt,
            completion=completion,
            system_prompt=system_prompt,
        )

        assert isinstance(sft, dict)
        assert "messages" in sft
        assert len(sft["messages"]) == 3
        assert sft["messages"][0] == {"role": "system", "content": system_prompt}
        assert sft["messages"][1] == {"role": "user", "content": user_prompt}
        assert sft["messages"][2] == {"role": "assistant", "content": completion}

    def test_format_sft_turn_validation_failure(self):
        with pytest.raises(ValueError):
            TrainingDataFormatter.format_sft_turn(
                prompt="   ",
                completion="resp",
                system_prompt="sys",
            )
        with pytest.raises(ValueError):
            TrainingDataFormatter.format_sft_turn(
                prompt="prompt",
                completion=" ",
                system_prompt="sys",
            )

    def test_format_dpo_pair(self):
        dpo = TrainingDataFormatter.format_dpo_pair(
            prompt="Plan my morning.",
            chosen="Here is a structured morning routine: 1. Hydrate 2. Meditate",
            rejected="Just do whatever you want.",
            system_prompt="You are a helpful planner.",
        )

        assert isinstance(dpo, dict)
        assert "prompt" in dpo
        assert "chosen" in dpo
        assert "rejected" in dpo
        assert "<|im_start|>system\nYou are a helpful planner." in dpo["prompt"]
        assert "<|im_start|>user\nPlan my morning." in dpo["prompt"]
        assert "Hydrate 2. Meditate<|im_end|>" in dpo["chosen"]
        assert "whatever you want.<|im_end|>" in dpo["rejected"]

    def test_format_dpo_pair_identical_responses_rejected(self):
        with pytest.raises(ValueError, match="cannot be identical"):
            TrainingDataFormatter.format_dpo_pair(
                prompt="test",
                chosen="Same response",
                rejected="Same response",
                system_prompt="sys",
            )

    def test_format_dpo_pair_empty_rejected_rejected(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            TrainingDataFormatter.format_dpo_pair(
                prompt="test",
                chosen="Good response",
                rejected="   ",
                system_prompt="sys",
            )

    def test_prepare_dataset_from_records(self):
        records = [
            {"prompt": "Task 1", "completion": "Done 1"},
            {"prompt": "Task 2", "completion": ""},  # invalid
            {"prompt": "Task 3", "completion": "Done 3"},
        ]
        sft_records = TrainingDataFormatter.prepare_dataset_from_records(records, dataset_type="sft")
        assert len(sft_records) == 2


class TestTrainingProfile:
    """Tests for LoRA/QLoRA configuration profiles and validation."""

    def test_default_profile_values(self):
        profile = TrainingProfile(dataset_version="v1.0.0-snapshot")
        assert profile.base_model_name == "Qwen/Qwen2.5-3B-Instruct"
        assert profile.use_qlora_4bit is True
        assert profile.lora_rank == 16
        assert profile.lora_alpha == 32
        assert profile.lora_dropout == 0.05
        assert len(profile.target_modules) == 7
        assert "q_proj" in profile.target_modules
        assert profile.learning_rate == 2e-4
        assert profile.max_seq_length == 2048
        assert profile.seed == 42

    def test_invalid_lora_rank_rejected(self):
        with pytest.raises(ValidationError):
            TrainingProfile(dataset_version="v1.0.0", lora_rank=0)
        with pytest.raises(ValidationError):
            TrainingProfile(dataset_version="v1.0.0", lora_rank=2048)

    def test_invalid_learning_rate_rejected(self):
        with pytest.raises(ValidationError):
            TrainingProfile(dataset_version="v1.0.0", learning_rate=0.5)

    def test_export_dict(self):
        profile = TrainingProfile(dataset_version="v1.0.0")
        data = profile.to_training_args_dict()
        assert data["learning_rate"] == 2e-4
        assert "seed" in data


class TestOllamaExporter:
    """Tests for Ollama Modelfile generation and export instructions."""

    def test_generate_modelfile_content(self, tmp_path):
        out_dir = str(tmp_path / "ollama_model")
        modelfile_path = OllamaExporter.generate_modelfile(
            gguf_model_path="models/qwen2.5-3b-lifeos.gguf",
            output_dir=out_dir,
            model_name="qwen2.5:3b-lifeos",
        )
        assert os.path.exists(modelfile_path)
        with open(modelfile_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "FROM models/qwen2.5-3b-lifeos.gguf" in content
        assert "PARAMETER temperature 0.7" in content
        assert "PARAMETER num_ctx 4096" in content
        assert "PARAMETER stop \"<|im_start|>\"" in content
        assert "PARAMETER stop \"<|im_end|>\"" in content
        assert "SYSTEM" in content
        assert "LifeOS" in content

    def test_get_packaging_instructions(self):
        instructions = OllamaExporter.get_packaging_instructions(
            adapter_dir="./output/adapter",
            output_dir="./output/export",
            model_tag="qwen2.5:3b-lifeos",
        )
        assert instructions["model_tag"] == "qwen2.5:3b-lifeos"
        assert len(instructions["steps"]) == 4
        assert "convert_hf_to_gguf.py" in instructions["steps"][1]["command"]
        assert "ollama create qwen2.5:3b-lifeos" in instructions["steps"][2]["command"]


class TestTrainingRunnerDryRun:
    """Tests for end-to-end dry-run execution using dataset version snapshots."""

    def test_dry_run_pipeline_success(self, app):
        with app.app_context():
            from app.models.user import User
            from app.models.user_preference import UserPreference
            from app.models.ai import AITrainingSample
            from app.extensions import db
            from app.services.ai_dataset_service import AIDatasetService

            # 1. Create a test user with active training consent
            user = User(
                email="trainer@lifeos.internal",
                full_name="Trainer Admin",
                password_hash="fake_hash"
            )
            db.session.add(user)
            db.session.flush()

            pref = UserPreference(
                user_id=user.id,
                ai_training_consent=True
            )
            db.session.add(pref)

            # 2. Add an approved, sanitized, valid training sample
            sample = AITrainingSample(
                user_id=user.id,
                prompt_input="Help me prioritize my morning tasks",
                chosen_response="Here is your prioritized morning schedule: 1. Deep work 2. Email triage",
                category="productivity",
                dataset_type="sft",
                consent_status="granted",
                review_status="approved",
                validation_status="valid",
                sanitization_status="sanitized",
                quality_score=1.0
            )
            db.session.add(sample)
            db.session.commit()

            # 3. Create dataset version snapshot
            dataset_service = AIDatasetService()
            version_name = "v1.0.0-training-test"
            dataset_service.create_version_snapshot(
                version_name=version_name,
                description="Test snapshot for fine-tuning pipeline",
                dataset_type="sft",
                created_by_user_id=user.id
            )

            # 4. Run the dry-run pipeline
            runner = TrainingPipelineRunner(dataset_service=dataset_service)
            profile = TrainingProfile(dataset_version=version_name, dataset_type="sft")
            result = runner.run_pipeline(profile=profile, dry_run=True)

            assert result["status"] == "validated"
            assert result["mode"] == "dry_run"
            assert result["dataset_version"] == version_name
            assert result["eligible_sample_count"] >= 1
            assert "target_modules" in result
            assert "hardware_detected" in result
            assert result["dataset_export_hash"] is not None
