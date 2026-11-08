"""LifeOS - AI Prompt Version Repository Layer.

Handles database operations, concurrency-safe transactions, and immutability
enforcement for AI system prompt templates.
"""
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import desc
from app.extensions import db
from app.models.ai import AIPromptVersion, AIMessage
from app.core.exceptions import BadRequestException


class AIPromptRepository:
    """Repository handling CRUD and transactional activations for AIPromptVersion."""

    def create(
        self,
        version_tag: str,
        prompt_template: str,
        change_summary: str,
        created_by: Optional[str] = None,
        is_active: bool = False
    ) -> AIPromptVersion:
        """Create and persist a new immutable prompt version."""
        version = AIPromptVersion(
            version_tag=version_tag,
            prompt_template=prompt_template,
            change_summary=change_summary,
            created_by=created_by,
            is_active=False
        )
        db.session.add(version)
        db.session.flush()

        if is_active:
            self.activate(version)
        else:
            db.session.commit()

        return version

    def get_by_id(self, version_id: str) -> Optional[AIPromptVersion]:
        """Retrieve prompt version by primary key ID."""
        return db.session.get(AIPromptVersion, version_id)

    def get_by_version_tag(self, version_tag: str) -> Optional[AIPromptVersion]:
        """Retrieve prompt version by unique semantic tag."""
        return AIPromptVersion.query.filter_by(version_tag=version_tag).first()

    def get_active(self) -> Optional[AIPromptVersion]:
        """Retrieve the single currently active prompt version."""
        return AIPromptVersion.query.filter_by(is_active=True).first()

    def list_versions(self, limit: int = 20, offset: int = 0) -> Tuple[List[AIPromptVersion], int]:
        """Retrieve paginated prompt versions ordered by creation timestamp descending."""
        query = AIPromptVersion.query
        total = query.count()
        items = (
            query
            .order_by(desc(AIPromptVersion.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def activate(self, version: AIPromptVersion) -> AIPromptVersion:
        """Transactionally promote a version to active while deactivating any predecessor.

        Uses row-level locking (with_for_update) to guarantee atomicity and avoid
        partial unique index collisions on `uq_ai_prompt_versions_active`.
        Does not mutate the prompt's template or tag content.
        """
        # Lock any existing active version(s)
        current_active = (
            AIPromptVersion.query
            .filter_by(is_active=True)
            .with_for_update()
            .all()
        )

        for existing in current_active:
            if existing.id != version.id:
                existing.is_active = False

        db.session.flush()

        # Activate target version
        version.is_active = True
        version.activated_at = datetime.now(timezone.utc)
        db.session.commit()
        return version

    def delete_if_unreferenced(self, version: AIPromptVersion) -> None:
        """Safely delete an unreferenced inactive prompt version.

        Guarantees that active or historical prompt versions attributed to
        past messages are never deleted.
        """
        if version.is_active:
            raise BadRequestException(
                "Cannot delete currently active prompt version. Deactivate or activate another version first."
            )

        has_references = (
            db.session.query(AIMessage.id)
            .filter_by(prompt_version_id=version.id)
            .first()
            is not None
        )
        if has_references:
            raise BadRequestException(
                "Cannot delete prompt version: it is referenced by existing AI messages. "
                "Historical prompt attribution must be preserved."
            )

        db.session.delete(version)
        db.session.commit()

