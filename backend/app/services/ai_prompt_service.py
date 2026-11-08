"""LifeOS - AI Prompt Versioning Service Layer.

Provides lifecycle controls, baseline initialization, activation,
rollback, and historical immutability guarantees for AI system prompts.
"""
from typing import Optional, Dict, Any
from app.repositories.ai_prompt_repository import AIPromptRepository
from app.models.ai import AIPromptVersion
from app.ai.workflow import SYSTEM_PROMPT_TEMPLATE
from app.core.exceptions import NotFoundException, BadRequestException


class AIPromptService:
    """Service orchestrating immutable prompt versions and activation state."""

    def __init__(self, prompt_repo: Optional[AIPromptRepository] = None):
        self.prompt_repo = prompt_repo or AIPromptRepository()

    def create_version(
        self,
        version_tag: str,
        prompt_template: str,
        change_summary: str,
        created_by: Optional[str] = None,
        activate_immediately: bool = False
    ) -> AIPromptVersion:
        """Create a new immutable prompt version.

        Rejects duplicate version tags. Once created, prompt content cannot be modified.
        """
        existing = self.prompt_repo.get_by_version_tag(version_tag)
        if existing:
            raise BadRequestException(f"Prompt version with tag '{version_tag}' already exists")

        return self.prompt_repo.create(
            version_tag=version_tag,
            prompt_template=prompt_template,
            change_summary=change_summary,
            created_by=created_by,
            is_active=activate_immediately
        )

    def get_version_by_id(self, version_id: str) -> AIPromptVersion:
        """Retrieve a prompt version by ID."""
        version = self.prompt_repo.get_by_id(version_id)
        if not version:
            raise NotFoundException(f"Prompt version with ID '{version_id}' not found")
        return version

    def get_active_prompt(self) -> Optional[AIPromptVersion]:
        """Retrieve the currently active prompt version, if any."""
        return self.prompt_repo.get_active()

    def get_active_prompt_or_initialize(self) -> AIPromptVersion:
        """Retrieve the currently active prompt version or initialize the default baseline.

        Guarantees that there is always an active, valid prompt version in the database
        for LangGraph chat executions.
        """
        active = self.prompt_repo.get_active()
        if active:
            return active

        # Check if default baseline already exists
        baseline = self.prompt_repo.get_by_version_tag("v1.0.0-baseline")
        if baseline:
            return self.prompt_repo.activate(baseline)

        # Create and activate baseline
        return self.prompt_repo.create(
            version_tag="v1.0.0-baseline",
            prompt_template=SYSTEM_PROMPT_TEMPLATE,
            change_summary="System prompt baseline initialization",
            created_by=None,
            is_active=True
        )

    def activate_version(self, version_id: str) -> AIPromptVersion:
        """Transactionally promote a specific prompt version to active."""
        version = self.get_version_by_id(version_id)
        if version.is_active:
            return version  # Idempotent activation

        return self.prompt_repo.activate(version)

    def rollback_to_tag(self, version_tag: str) -> AIPromptVersion:
        """Roll back to an older prompt version by activating its tag."""
        version = self.prompt_repo.get_by_version_tag(version_tag)
        if not version:
            raise NotFoundException(f"Prompt version with tag '{version_tag}' not found")

        return self.prompt_repo.activate(version)

    def list_versions(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """List all prompt versions with pagination."""
        items, total = self.prompt_repo.list_versions(
            limit=min(max(limit, 1), 100),
            offset=max(offset, 0)
        )
        return {
            "prompts": [p.to_dict() for p in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

