from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Float, Integer, JSON, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class AIConversation(BaseModel):
    """Chat thread containing exchanges between the user and LifeOS Local AI."""
    __tablename__ = "ai_conversations"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        default="New Conversation",
        nullable=False
    )
    model_used: Mapped[str] = mapped_column(
        String(50),
        default="qwen2.5:3b",
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_conversations")
    messages: Mapped[list["AIMessage"]] = relationship(
        "AIMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AIMessage.created_at"
    )

    __table_args__ = (
        Index("ix_ai_conversations_user_created", "user_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "model_used": self.model_used,
            "messages_count": len(self.messages) if self.messages else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIPromptVersion(BaseModel):
    """Immutable versioned registry of system prompt templates."""
    __tablename__ = "ai_prompt_versions"

    version_tag: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    prompt_template: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    change_summary: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    messages: Mapped[list["AIMessage"]] = relationship(
        "AIMessage",
        back_populates="prompt_version"
    )
    evaluation_runs: Mapped[list["AIEvaluationRun"]] = relationship(
        "AIEvaluationRun",
        back_populates="prompt_version"
    )

    __table_args__ = (
        Index(
            "uq_ai_prompt_versions_active",
            "is_active",
            unique=True,
            postgresql_where=(is_active.is_(True)),
            sqlite_where=(is_active.is_(True)),
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_tag": self.version_tag,
            "prompt_template": self.prompt_template,
            "change_summary": self.change_summary,
            "created_by": self.created_by,
            "is_active": self.is_active,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIMessage(BaseModel):
    """Individual dialogue turn in an AI conversation."""
    __tablename__ = "ai_messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    prompt_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_prompt_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # user, assistant, system, tool
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    tool_calls: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )
    tokens_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # Relationships
    conversation: Mapped[AIConversation] = relationship("AIConversation", back_populates="messages")
    prompt_version: Mapped[Optional["AIPromptVersion"]] = relationship("AIPromptVersion", back_populates="messages")
    feedback: Mapped[Optional["AIFeedback"]] = relationship(
        "AIFeedback",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan"
    )
    evaluation_runs: Mapped[list["AIEvaluationRun"]] = relationship(
        "AIEvaluationRun",
        back_populates="message",
        cascade="all, delete-orphan"
    )
    training_samples: Mapped[list["AITrainingSample"]] = relationship(
        "AITrainingSample",
        back_populates="source_message"
    )

    __table_args__ = (
        Index("ix_ai_messages_conv_created", "conversation_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "prompt_version_id": self.prompt_version_id,
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AIFeedback(BaseModel):
    """User feedback, rating, and correction for an individual assistant turn."""
    __tablename__ = "ai_feedback"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    message_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_messages.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )  # +1 (positive) or -1 (negative)
    feedback_type: Mapped[str] = mapped_column(
        String(30),
        default="thumbs",
        nullable=False
    )  # thumbs_up, thumbs_down, correction, issue_report
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )  # hallucination, inaccurate_schedule, unhelpful, formatting, other
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    suggested_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_feedback")
    message: Mapped["AIMessage"] = relationship("AIMessage", back_populates="feedback")
    training_samples: Mapped[list["AITrainingSample"]] = relationship(
        "AITrainingSample",
        back_populates="source_feedback"
    )

    __table_args__ = (
        Index("ix_ai_feedback_user_created", "user_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message_id": self.message_id,
            "rating": self.rating,
            "feedback_type": self.feedback_type,
            "category": self.category,
            "comment": self.comment,
            "suggested_response": self.suggested_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIEvaluationRun(BaseModel):
    """Parent benchmark evaluation execution for an assistant response."""
    __tablename__ = "ai_evaluation_runs"

    message_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    prompt_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_prompt_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    model_name: Mapped[str] = mapped_column(
        String(50),
        default="qwen2.5:3b",
        nullable=False
    )
    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    message: Mapped["AIMessage"] = relationship("AIMessage", back_populates="evaluation_runs")
    prompt_version: Mapped[Optional["AIPromptVersion"]] = relationship("AIPromptVersion", back_populates="evaluation_runs")
    metrics: Mapped[list["AIEvaluationMetric"]] = relationship(
        "AIEvaluationMetric",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="AIEvaluationMetric.created_at"
    )

    __table_args__ = (
        Index("ix_ai_eval_runs_msg_created", "message_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "prompt_version_id": self.prompt_version_id,
            "model_name": self.model_name,
            "passed": self.passed,
            "overall_score": self.overall_score,
            "notes": self.notes,
            "metrics": [m.to_dict() for m in self.metrics] if self.metrics else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIEvaluationMetric(BaseModel):
    """Individual dimension metric result belonging to an evaluation run."""
    __tablename__ = "ai_evaluation_metrics"

    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_evaluation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    metric_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # relevance, factual_consistency, instruction_following, completeness, clarity, hallucination_risk, personalization_quality
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )  # 0.0 to 1.0
    passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationship
    run: Mapped["AIEvaluationRun"] = relationship("AIEvaluationRun", back_populates="metrics")

    __table_args__ = (
        Index("ix_ai_eval_metrics_run_name", "run_id", "metric_name"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "metric_name": self.metric_name,
            "score": self.score,
            "passed": self.passed,
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AITrainingSample(BaseModel):
    """Curated instruction-tuning / preference training sample."""
    __tablename__ = "ai_training_samples"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    source_feedback_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_feedback.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    source_message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    prompt_input: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    chosen_response: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    rejected_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    dataset_type: Mapped[str] = mapped_column(
        String(20),
        default="sft",
        nullable=False
    )  # sft, dpo
    consent_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, granted, revoked
    review_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, approved, rejected
    quality_score: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    sanitization_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, sanitized, rejected
    validation_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, valid, invalid
    validation_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    dataset_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_dataset_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_training_samples")
    source_feedback: Mapped[Optional["AIFeedback"]] = relationship(
        "AIFeedback",
        back_populates="training_samples"
    )
    source_message: Mapped[Optional["AIMessage"]] = relationship(
        "AIMessage",
        back_populates="training_samples"
    )
    dataset_version: Mapped[Optional["AIDatasetVersion"]] = relationship(
        "AIDatasetVersion",
        back_populates="samples"
    )

    __table_args__ = (
        Index("ix_ai_training_samples_user_review", "user_id", "review_status"),
        Index("ix_ai_training_samples_consent_review", "consent_status", "review_status"),
        Index("ix_ai_training_samples_val_san", "validation_status", "sanitization_status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source_feedback_id": self.source_feedback_id,
            "source_message_id": self.source_message_id,
            "prompt_input": self.prompt_input,
            "chosen_response": self.chosen_response,
            "rejected_response": self.rejected_response,
            "category": self.category,
            "dataset_type": self.dataset_type,
            "consent_status": self.consent_status,
            "review_status": self.review_status,
            "sanitization_status": self.sanitization_status,
            "validation_status": self.validation_status,
            "validation_notes": self.validation_notes,
            "dataset_version_id": self.dataset_version_id,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIDatasetVersion(BaseModel):
    """Immutable versioned snapshot of curated, validated, and sanitized training data."""
    __tablename__ = "ai_dataset_versions"

    version_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    sample_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    dataset_type: Mapped[str] = mapped_column(
        String(20),
        default="sft",
        nullable=False
    )  # sft, dpo, mixed
    manifest_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )  # SHA-256 checksum of export contents
    included_categories: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True
    )
    validation_summary: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )
    is_exported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    exported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    samples: Mapped[list["AITrainingSample"]] = relationship(
        "AITrainingSample",
        back_populates="dataset_version"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_name": self.version_name,
            "description": self.description,
            "sample_count": self.sample_count,
            "dataset_type": self.dataset_type,
            "manifest_hash": self.manifest_hash,
            "included_categories": self.included_categories or [],
            "validation_summary": self.validation_summary or {},
            "is_exported": self.is_exported,
            "exported_at": self.exported_at.isoformat() if self.exported_at else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }



class AIMemory(BaseModel):
    """Extracted contextual memories, preferences, and facts retained by the local AI."""
    __tablename__ = "ai_memories"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    memory_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    memory_value: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    memory_type: Mapped[str] = mapped_column(
        String(30),
        default="preference",
        nullable=False
    )  # preference, personal_context, goal_decision, routine_pattern, fact
    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="confirmed",
        nullable=False,
        index=True
    )  # pending, confirmed, archived, rejected
    source_conversation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_conversations.id", ondelete="SET NULL"),
        nullable=True
    )
    source_message_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_messages.id", ondelete="SET NULL"),
        nullable=True
    )
    embedding: Mapped[dict | list | None] = mapped_column(
        JSON,
        nullable=True
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ai_memories")
    source_conversation: Mapped[Optional["AIConversation"]] = relationship("AIConversation")
    source_message: Mapped[Optional["AIMessage"]] = relationship("AIMessage")

    __table_args__ = (
        Index("ix_ai_memories_user_key", "user_id", "memory_key"),
        Index("ix_ai_memories_user_type", "user_id", "memory_type"),
        Index("ix_ai_memories_user_status", "user_id", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "memory_key": self.memory_key,
            "memory_value": self.memory_value,
            "memory_type": self.memory_type,
            "confidence": self.confidence,
            "status": self.status,
            "source_conversation_id": self.source_conversation_id,
            "source_message_id": self.source_message_id,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIModelVersion(BaseModel):
    """Registered AI Model version tracking lifecycle, evaluation metrics, and active runtime state."""
    __tablename__ = "ai_model_versions"

    model_tag: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )  # e.g., 'qwen2.5:3b', 'qwen2.5:3b-lifeos:v1'
    base_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Qwen/Qwen2.5-3B-Instruct"
    )
    version_tag: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # semantic version tag, e.g. 'v1.0.0'
    training_run_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )
    dataset_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    artifact_checksum: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )  # SHA-256 checksum of adapter or GGUF
    status: Mapped[str] = mapped_column(
        String(30),
        default="registered",
        nullable=False
    )  # registered, candidate, evaluated, approved, active, rejected, archived
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    evaluation_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    evaluation_report_path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    activated_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    __table_args__ = (
        Index("ix_ai_model_versions_status", "status"),
        Index("ix_ai_model_versions_active", "is_active"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "model_tag": self.model_tag,
            "base_model": self.base_model,
            "version_tag": self.version_tag,
            "training_run_id": self.training_run_id,
            "dataset_version": self.dataset_version,
            "artifact_checksum": self.artifact_checksum,
            "status": self.status,
            "is_active": self.is_active,
            "evaluation_score": self.evaluation_score,
            "evaluation_report_path": self.evaluation_report_path,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "activated_by": self.activated_by,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIModelRollbackLog(BaseModel):
    """Audit log tracking model activation and rollback events."""
    __tablename__ = "ai_model_rollback_logs"

    from_model_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("ai_model_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    to_model_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_model_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )  # 'activation', 'rollback'
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    executed_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        Index("ix_ai_model_rollback_logs_action", "action"),
        Index("ix_ai_model_rollback_logs_created", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "from_model_id": self.from_model_id,
            "to_model_id": self.to_model_id,
            "action": self.action,
            "reason": self.reason,
            "executed_by": self.executed_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AITrainingJob(BaseModel):
    """Orchestration record for continuous model training jobs."""
    __tablename__ = "ai_training_jobs"

    job_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    dataset_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    base_model_name: Mapped[str] = mapped_column(
        String(100),
        default="Qwen/Qwen2.5-3B-Instruct",
        nullable=False
    )
    candidate_model_tag: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    training_mode: Mapped[str] = mapped_column(
        String(20),
        default="qlora_4bit",
        nullable=False
    )  # qlora_4bit, lora_fp16
    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False
    )  # pending, validating, ready, running, completed, failed, cancelled
    config_payload: Mapped[Dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True
    )
    log_output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    artifact_checksum: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )
    artifact_directory: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    dataset_version: Mapped["AIDatasetVersion"] = relationship("AIDatasetVersion")
    created_by: Mapped[Optional["User"]] = relationship("User")

    __table_args__ = (
        Index("ix_ai_training_jobs_status", "status"),
        Index("ix_ai_training_jobs_dataset", "dataset_version_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "job_name": self.job_name,
            "dataset_version_id": self.dataset_version_id,
            "dataset_version_name": self.dataset_version.version_name if self.dataset_version else None,
            "base_model_name": self.base_model_name,
            "candidate_model_tag": self.candidate_model_tag,
            "training_mode": self.training_mode,
            "status": self.status,
            "config_payload": self.config_payload,
            "log_output": self.log_output,
            "error_message": self.error_message,
            "artifact_checksum": self.artifact_checksum,
            "artifact_directory": self.artifact_directory,
            "created_by_user_id": self.created_by_user_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


