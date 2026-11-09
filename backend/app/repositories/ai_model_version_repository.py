"""LifeOS - AI Model Version Repository (Step 10).

Data access layer for AIModelVersion registry and AIModelRollbackLog audit trail.
"""
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import desc
from app.extensions import db
from app.models.ai import AIModelVersion, AIModelRollbackLog


class AIModelVersionRepository:
    """Repository handling database operations for AI model version registry and rollback logs."""

    def get_by_id(self, model_id: str) -> Optional[AIModelVersion]:
        """Fetch model version by primary key UUID."""
        return db.session.get(AIModelVersion, model_id)

    def get_by_model_tag(self, model_tag: str) -> Optional[AIModelVersion]:
        """Fetch model version by unique Ollama model tag (e.g. 'qwen2.5:3b')."""
        return AIModelVersion.query.filter_by(model_tag=model_tag).first()

    def get_active_model(self) -> Optional[AIModelVersion]:
        """Retrieve currently active runtime model record."""
        return AIModelVersion.query.filter_by(is_active=True).first()

    def list_models(
        self,
        status: Optional[str] = None,
        base_model: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[AIModelVersion], int]:
        """List and paginate registered model versions."""
        query = AIModelVersion.query

        if status:
            query = query.filter(AIModelVersion.status == status)
        if base_model:
            query = query.filter(AIModelVersion.base_model == base_model)

        total = query.count()
        items = (
            query
            .order_by(desc(AIModelVersion.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def create_model_version(
        self,
        model_tag: str,
        version_tag: str,
        base_model: str = "Qwen/Qwen2.5-3B-Instruct",
        training_run_id: Optional[str] = None,
        dataset_version: Optional[str] = None,
        artifact_checksum: Optional[str] = None,
        status: str = "registered",
        is_active: bool = False,
        notes: Optional[str] = None,
    ) -> AIModelVersion:
        """Register a new AI model version."""
        record = AIModelVersion(
            model_tag=model_tag,
            version_tag=version_tag,
            base_model=base_model,
            training_run_id=training_run_id,
            dataset_version=dataset_version,
            artifact_checksum=artifact_checksum,
            status=status,
            is_active=is_active,
            notes=notes,
        )
        db.session.add(record)
        db.session.commit()
        return record

    def update_model_status(
        self,
        model: AIModelVersion,
        status: str,
        notes: Optional[str] = None
    ) -> AIModelVersion:
        """Update lifecycle status of a model version."""
        model.status = status
        if notes:
            model.notes = notes
        model.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return model

    def set_active_model(
        self,
        new_active_model: AIModelVersion,
        previous_active_model: Optional[AIModelVersion],
        action: str,
        reason: str,
        executed_by: Optional[str] = None
    ) -> AIModelRollbackLog:
        """Atomically transition active model and write audit log."""
        if previous_active_model:
            previous_active_model.is_active = False
            # If previous model was active, revert status to approved
            if previous_active_model.status == "active":
                previous_active_model.status = "approved"
            previous_active_model.updated_at = datetime.now(timezone.utc)

        new_active_model.is_active = True
        new_active_model.status = "active"
        new_active_model.activated_by = executed_by
        new_active_model.activated_at = datetime.now(timezone.utc)
        new_active_model.updated_at = datetime.now(timezone.utc)

        # Create audit log
        log_entry = AIModelRollbackLog(
            from_model_id=previous_active_model.id if previous_active_model else None,
            to_model_id=new_active_model.id,
            action=action,
            reason=reason,
            executed_by=executed_by
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

    def list_audit_logs(self, limit: int = 20, offset: int = 0) -> Tuple[List[AIModelRollbackLog], int]:
        """Fetch audit trail for activations and rollbacks."""
        query = AIModelRollbackLog.query
        total = query.count()
        items = (
            query
            .order_by(desc(AIModelRollbackLog.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

