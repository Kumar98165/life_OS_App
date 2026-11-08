"""LifeOS - Automation Models.

Normalized relational models for advanced AI automation:
- AutomationDefinition: Template or user-specific automation configuration
- AutomationExecution: Discrete run/lifecycle of an automation
- AutomationAction: Proposed, approved, or executed actions with risk scoring
- AutomationApproval: Human-in-the-loop approval gate with expiration & tokens
- AutomationExecutionLog: Append-only execution audit trail and diagnostics
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Text, Boolean, Integer, DateTime, ForeignKey, Index, UniqueConstraint, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel, utc_now
from app.extensions import db


# -----------------------------------------------------------------------------
# Automation Definition (Templates & User Configs)
# -----------------------------------------------------------------------------

class AutomationDefinition(BaseModel):
    """Configuration or template defining an automated AI workflow."""
    __tablename__ = "automation_definitions"

    # Owning user (NULL for system templates)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Human-readable identifier/slug (e.g., 'plan_my_day', 'habit_recovery')
    slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(32), default="productivity", nullable=False)  # productivity, review, health, finance

    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Scheduling settings (e.g., daily at 08:00, weekly on Sunday at 18:00)
    trigger_type: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)  # manual, scheduled, event
    cron_expression: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    scheduled_time: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)  # HH:MM (local user time)
    scheduled_days: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # daily, weekdays, monday, sunday

    # Configuration parameters (JSON schema options)
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Operational metrics
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    executions: Mapped[List["AutomationExecution"]] = relationship(
        "AutomationExecution",
        back_populates="definition",
        cascade="all, delete-orphan",
        order_by="desc(AutomationExecution.created_at)"
    )

    __table_args__ = (
        Index("ix_auto_def_user_slug", "user_id", "slug"),
        Index("ix_auto_def_active_sched", "is_active", "is_paused", "trigger_type"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "is_template": self.is_template,
            "is_active": self.is_active,
            "is_paused": self.is_paused,
            "trigger_type": self.trigger_type,
            "cron_expression": self.cron_expression,
            "scheduled_time": self.scheduled_time,
            "scheduled_days": self.scheduled_days,
            "configuration": self.configuration or {},
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# -----------------------------------------------------------------------------
# Automation Execution (Lifecycle Run)
# -----------------------------------------------------------------------------

class AutomationExecution(BaseModel):
    """Single execution lifecycle instance of an automation workflow."""
    __tablename__ = "automation_executions"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    definition_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("automation_definitions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Idempotency token to guard against duplicate runs
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    # Trigger source: manual, scheduled, assistant_prompt
    triggered_by: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)

    # Execution status:
    # pending, planning, awaiting_approval, executing, completed, failed, cancelled, paused
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)

    # Maximum risk tier among planned actions: low, medium, high
    risk_level: Mapped[str] = mapped_column(String(16), default="low", nullable=False)

    # Snapshot of inputs & state context
    trigger_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated narrative response
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timing metrics
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Retry count
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Relationships
    definition: Mapped[Optional[AutomationDefinition]] = relationship(
        "AutomationDefinition",
        back_populates="executions"
    )
    actions: Mapped[List["AutomationAction"]] = relationship(
        "AutomationAction",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="AutomationAction.sequence_order"
    )
    approvals: Mapped[List["AutomationApproval"]] = relationship(
        "AutomationApproval",
        back_populates="execution",
        cascade="all, delete-orphan"
    )
    logs: Mapped[List["AutomationExecutionLog"]] = relationship(
        "AutomationExecutionLog",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="AutomationExecutionLog.created_at"
    )

    __table_args__ = (
        Index("ix_auto_exec_user_status", "user_id", "status"),
        Index("ix_auto_exec_idemp", "user_id", "idempotency_key", unique=False),
    )

    def to_dict(self, include_children: bool = True) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "definition_id": self.definition_id,
            "definition_title": self.definition.title if self.definition else None,
            "definition_slug": self.definition.slug if self.definition else None,
            "idempotency_key": self.idempotency_key,
            "triggered_by": self.triggered_by,
            "status": self.status,
            "risk_level": self.risk_level,
            "trigger_payload": self.trigger_payload or {},
            "summary": self.summary,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_duration_ms": self.execution_duration_ms,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_children:
            data["actions"] = [a.to_dict() for a in self.actions]
            data["approvals"] = [ap.to_dict() for ap in self.approvals]
            data["logs"] = [lg.to_dict() for lg in self.logs]
        return data


# -----------------------------------------------------------------------------
# Automation Action (Proposed/Executed Operation)
# -----------------------------------------------------------------------------

class AutomationAction(BaseModel):
    """A discrete operation planned by the AI model within an execution."""
    __tablename__ = "automation_actions"

    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("automation_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tool invocation metadata
    sequence_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(64), nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g., create_task, schedule_block, create_reminder
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    # Risk tier:
    # low: read-only summary/insight (auto-executed)
    # medium: create task, block, reminder (requires confirmation)
    # high: update/delete records, finance modifications (blocked or strictly confirmed)
    risk_level: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Action parameters and verified output
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # State: pending, awaiting_approval, approved, rejected, executed, failed, skipped
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    execution: Mapped[AutomationExecution] = relationship(
        "AutomationExecution",
        back_populates="actions"
    )
    approval: Mapped[Optional["AutomationApproval"]] = relationship(
        "AutomationApproval",
        back_populates="action",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "user_id": self.user_id,
            "sequence_order": self.sequence_order,
            "tool_name": self.tool_name,
            "action_type": self.action_type,
            "description": self.description,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
            "parameters": self.parameters or {},
            "result_payload": self.result_payload,
            "status": self.status,
            "error_message": self.error_message,
            "has_approval": self.approval is not None,
            "approval_id": self.approval.id if self.approval else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# -----------------------------------------------------------------------------
# Automation Approval (Human-in-the-Loop Gate)
# -----------------------------------------------------------------------------

class AutomationApproval(BaseModel):
    """Explicit human approval record bound to an action and its exact parameters."""
    __tablename__ = "automation_approvals"

    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("automation_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("automation_actions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Approval state: pending, approved, rejected, expired, cancelled
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)

    # Cryptographic/hash signature of exact proposed action + parameters
    parameter_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Proposed diff / summary shown to user before approving
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Approval expiration (e.g. 24 hours from creation)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: utc_now() + timedelta(hours=24),
        nullable=False,
        index=True
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    execution: Mapped[AutomationExecution] = relationship(
        "AutomationExecution",
        back_populates="approvals"
    )
    action: Mapped[AutomationAction] = relationship(
        "AutomationAction",
        back_populates="approval"
    )

    @property
    def is_expired(self) -> bool:
        """Evaluate if the approval window has lapsed."""
        if not self.expires_at:
            return False
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return utc_now() > exp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "action_id": self.action_id,
            "user_id": self.user_id,
            "status": "expired" if (self.status == "pending" and self.is_expired) else self.status,
            "parameter_hash": self.parameter_hash,
            "change_summary": self.change_summary,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "decision_reason": self.decision_reason,
            "is_expired": self.is_expired,
            "action_summary": {
                "tool_name": self.action.tool_name if self.action else None,
                "action_type": self.action.action_type if self.action else None,
                "description": self.action.description if self.action else None,
                "risk_level": self.action.risk_level if self.action else "medium",
                "parameters": self.action.parameters if self.action else {},
            } if self.action else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# -----------------------------------------------------------------------------
# Automation Execution Log (Append-Only Audit Trail)
# -----------------------------------------------------------------------------

class AutomationExecutionLog(BaseModel):
    """Granular audit entry recorded during workflow execution steps."""
    __tablename__ = "automation_execution_logs"

    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("automation_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Step in the LangGraph workflow:
    # classification, context_retrieval, planning, risk_assessment,
    # approval_gate, execution, verification, response_generation
    step_name: Mapped[str] = mapped_column(String(64), nullable=False)
    level: Mapped[str] = mapped_column(String(16), default="info", nullable=False)  # info, warning, error
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    execution: Mapped[AutomationExecution] = relationship(
        "AutomationExecution",
        back_populates="logs"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "step_name": self.step_name,
            "level": self.level,
            "message": self.message,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
