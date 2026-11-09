"""LifeOS - Model Version Lifecycle & Rollback Service (Step 10).

Coordinates:
- Model version registration and semantic version validation
- Benchmark evaluation attachment and minimum score verification
- Model approval workflow
- Safe model activation with availability checks
- Instant rollback to previous approved model
- Strict role-based authorization for administrative operations
"""
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import requests

from app.models.ai import AIModelVersion, AIModelRollbackLog
from app.repositories.ai_model_version_repository import AIModelVersionRepository
from app.ai.config import check_ollama_health, get_ai_config, AIRuntimeConfig
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException,
)

# Valid lifecycle transitions
ALLOWED_TRANSITIONS = {
    "registered": {"candidate", "evaluated", "rejected", "archived"},
    "candidate": {"evaluated", "rejected", "archived"},
    "evaluated": {"approved", "rejected", "archived"},
    "approved": {"active", "archived", "rejected"},
    "active": {"approved", "archived"},
    "rejected": {"candidate", "archived"},
    "archived": set(),
}

# Minimum benchmark score required for human approval (e.g., 0.65)
MIN_BENCHMARK_APPROVAL_SCORE = 0.65


class ModelRegistryService:
    """Service layer managing AI model version registration, activation, and rollback."""

    def __init__(self, repo: Optional[AIModelVersionRepository] = None):
        self.repo = repo or AIModelVersionRepository()

    def _verify_admin(self, user: Any) -> None:
        """Enforce admin authorization for model lifecycle operations."""
        if not user:
            raise ForbiddenException("Authentication required.")
        role = getattr(user, "role", "user")
        if role != "admin":
            raise ForbiddenException("Only administrators can perform AI model version management.")

    def register_model(
        self,
        model_tag: str,
        version_tag: str,
        base_model: str = "Qwen/Qwen2.5-3B-Instruct",
        training_run_id: Optional[str] = None,
        dataset_version: Optional[str] = None,
        artifact_checksum: Optional[str] = None,
        notes: Optional[str] = None,
        user: Optional[Any] = None,
    ) -> AIModelVersion:
        """Register a new AI model version."""
        if user:
            self._verify_admin(user)

        model_tag = model_tag.strip()
        version_tag = version_tag.strip()

        if not model_tag:
            raise BadRequestException("Model tag cannot be empty.")
        if not version_tag:
            raise BadRequestException("Version tag cannot be empty.")

        # Validate semantic version pattern (e.g., v1.0.0 or 1.0.0)
        semver_regex = r"^v?\d+\.\d+\.\d+(-[a-zA-Z0-9_\.]+)?$"
        if not re.match(semver_regex, version_tag):
            raise BadRequestException(f"Invalid version_tag '{version_tag}'. Must follow semantic versioning (e.g. v1.0.0).")

        # Validate artifact checksum if provided (64-char hex SHA-256)
        if artifact_checksum:
            if not re.match(r"^[a-fA-F0-9]{64}$", artifact_checksum.strip()):
                raise BadRequestException("Invalid artifact_checksum. Must be a 64-character SHA-256 hexadecimal string.")

        # Ensure uniqueness of model_tag
        if self.repo.get_by_model_tag(model_tag):
            raise ConflictException(f"Model with tag '{model_tag}' is already registered.")

        return self.repo.create_model_version(
            model_tag=model_tag,
            version_tag=version_tag,
            base_model=base_model,
            training_run_id=training_run_id,
            dataset_version=dataset_version,
            artifact_checksum=artifact_checksum,
            status="registered",
            is_active=False,
            notes=notes,
        )

    def attach_evaluation_report(
        self,
        model_id: str,
        evaluation_score: float,
        report_path: Optional[str] = None,
        user: Optional[Any] = None,
    ) -> AIModelVersion:
        """Attach STEP 9 benchmark results to a registered model."""
        if user:
            self._verify_admin(user)

        model = self.repo.get_by_id(model_id)
        if not model:
            raise NotFoundException(f"Model version '{model_id}' not found.")

        if model.status not in ("registered", "candidate", "evaluated"):
            raise BadRequestException(f"Cannot attach evaluation to model in '{model.status}' state.")

        if not (0.0 <= evaluation_score <= 1.0):
            raise BadRequestException("Evaluation score must be between 0.0 and 1.0.")

        model.evaluation_score = evaluation_score
        model.evaluation_report_path = report_path
        model.status = "evaluated"
        return self.repo.update_model_status(model, status="evaluated", notes=model.notes)

    def approve_model(
        self,
        model_id: str,
        user: Any,
        notes: Optional[str] = None,
    ) -> AIModelVersion:
        """Approve an evaluated model for potential runtime activation."""
        self._verify_admin(user)

        model = self.repo.get_by_id(model_id)
        if not model:
            raise NotFoundException(f"Model version '{model_id}' not found.")

        if model.status != "evaluated":
            raise BadRequestException(f"Model must be in 'evaluated' status before approval (current: '{model.status}').")

        if model.evaluation_score is None:
            raise BadRequestException("Cannot approve a model with no benchmark evaluation score.")

        if model.evaluation_score < MIN_BENCHMARK_APPROVAL_SCORE:
            raise BadRequestException(
                f"Model evaluation score ({model.evaluation_score}) is below the minimum threshold ({MIN_BENCHMARK_APPROVAL_SCORE}) required for approval."
            )

        model.status = "approved"
        model.approved_by = user.id
        model.approved_at = datetime.now(timezone.utc)
        return self.repo.update_model_status(model, status="approved", notes=notes)

    def activate_model(
        self,
        model_id: str,
        user: Any,
        reason: str,
        allow_offline_mock: bool = False,
    ) -> AIModelRollbackLog:
        """Safely activate an approved model version into active runtime."""
        self._verify_admin(user)

        model = self.repo.get_by_id(model_id)
        if not model:
            raise NotFoundException(f"Model version '{model_id}' not found.")

        if model.status != "approved":
            raise BadRequestException(f"Only approved models can be activated (current status: '{model.status}').")

        if model.is_active:
            raise BadRequestException(f"Model '{model.model_tag}' is already the active model.")

        # Verify model presence in Ollama runtime
        if not allow_offline_mock:
            cfg = get_ai_config()
            try:
                resp = requests.get(f"{cfg['base_url'].rstrip('/')}/api/tags", timeout=5)
                if resp.status_code != 200:
                    raise BadRequestException(f"Ollama server returned HTTP {resp.status_code}. Cannot verify model.")
                models = [m.get("name", "") for m in resp.json().get("models", [])]
                found = any(
                    model.model_tag == m or model.model_tag == m.split(":")[0] or m.startswith(model.model_tag)
                    for m in models
                )
                if not found:
                    raise BadRequestException(
                        f"Model '{model.model_tag}' is not installed or available in Ollama runtime at {cfg['base_url']}. "
                        "Cannot activate an unavailable model."
                    )
            except requests.exceptions.RequestException as e:
                raise BadRequestException(f"Cannot connect to Ollama runtime at {cfg['base_url']} to verify model: {str(e)}")

        current_active = self.repo.get_active_model()
        log_entry = self.repo.set_active_model(
            new_active_model=model,
            previous_active_model=current_active,
            action="activation",
            reason=reason,
            executed_by=user.id
        )

        # Clear in-memory override so dynamic resolver reads new active record
        AIRuntimeConfig.set_runtime_override(None)

        return log_entry

    def rollback_model(
        self,
        target_model_id: str,
        user: Any,
        reason: str,
        allow_offline_mock: bool = False,
    ) -> AIModelRollbackLog:
        """Roll back active runtime model to a specified previously approved model."""
        self._verify_admin(user)

        if not reason or len(reason.strip()) < 5:
            raise BadRequestException("A detailed rollback reason (at least 5 characters) must be provided.")

        target_model = self.repo.get_by_id(target_model_id)
        if not target_model:
            raise NotFoundException(f"Target model version '{target_model_id}' not found.")

        if target_model.status not in ("approved", "active"):
            raise BadRequestException(f"Cannot roll back to model in '{target_model.status}' status. Model must be approved.")

        current_active = self.repo.get_active_model()
        if current_active and current_active.id == target_model.id:
            raise BadRequestException(f"Model '{target_model.model_tag}' is already the currently active model.")

        # Verify target model availability in Ollama
        if not allow_offline_mock:
            cfg = get_ai_config()
            try:
                resp = requests.get(f"{cfg['base_url'].rstrip('/')}/api/tags", timeout=5)
                if resp.status_code == 200:
                    models = [m.get("name", "") for m in resp.json().get("models", [])]
                    found = any(
                        target_model.model_tag == m or target_model.model_tag == m.split(":")[0] or m.startswith(target_model.model_tag)
                        for m in models
                    )
                    if not found:
                        raise BadRequestException(
                            f"Target rollback model '{target_model.model_tag}' is not found in Ollama runtime."
                        )
            except requests.exceptions.RequestException as e:
                raise BadRequestException(f"Ollama connection error during rollback verification: {str(e)}")

        log_entry = self.repo.set_active_model(
            new_active_model=target_model,
            previous_active_model=current_active,
            action="rollback",
            reason=reason,
            executed_by=user.id
        )

        AIRuntimeConfig.set_runtime_override(None)

        return log_entry

    def initialize_default_base_model(self) -> AIModelVersion:
        """Ensure active base model (qwen2.5:3b) is registered and active in the database."""
        existing = self.repo.get_by_model_tag("qwen2.5:3b")
        if existing:
            if not self.repo.get_active_model():
                existing.is_active = True
                existing.status = "active"
                self.repo.update_model_status(existing, status="active")
            return existing

        return self.repo.create_model_version(
            model_tag="qwen2.5:3b",
            version_tag="v1.0.0",
            base_model="Qwen/Qwen2.5-3B-Instruct",
            training_run_id=None,
            dataset_version=None,
            artifact_checksum=None,
            status="active",
            is_active=True,
            notes="Default base production Ollama model initialized.",
        )

