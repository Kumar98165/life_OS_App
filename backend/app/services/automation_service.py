"""LifeOS - Automation Service Layer.

Coordinates automation definition lifecycle, workflow execution, approval resolution,
scheduling integration, and operational commands (pause, resume, cancel).
"""
import uuid
import time
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import or_, and_, desc

from app import db
from app.models.automation import (
    AutomationDefinition,
    AutomationExecution,
    AutomationAction,
    AutomationApproval,
    AutomationExecutionLog
)
from app.models.user import User
from app.automation.templates import AUTOMATION_TEMPLATES
from app.automation.workflow import lifeos_automation_graph
from app.automation.tools import automation_tool_registry
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException
)
from app.core.security import check_resource_ownership


class AutomationService:
    """Central business engine for LifeOS AI Automations."""

    # -------------------------------------------------------------------------
    # Definition / Template Lifecycle
    # -------------------------------------------------------------------------

    def list_templates(self) -> List[Dict[str, Any]]:
        """List predefined automation templates."""
        return AUTOMATION_TEMPLATES

    def seed_default_templates(self) -> int:
        """Ensure system template records exist in automation_definitions."""
        count = 0
        for tpl in AUTOMATION_TEMPLATES:
            existing = AutomationDefinition.query.filter_by(slug=tpl["slug"], is_template=True).first()
            if not existing:
                definition = AutomationDefinition(
                    user_id=None,
                    slug=tpl["slug"],
                    title=tpl["title"],
                    category=tpl["category"],
                    description=tpl["description"],
                    is_template=True,
                    is_active=True,
                    is_paused=False,
                    trigger_type=tpl["trigger_type"],
                    scheduled_time=tpl["scheduled_time"],
                    scheduled_days=tpl["scheduled_days"],
                    configuration=tpl["configuration"],
                )
                db.session.add(definition)
                count += 1
        if count > 0:
            db.session.commit()
        return count

    def list_user_automations(self, user_id: str) -> List[Dict[str, Any]]:
        """List custom or configured automations for user, including active templates."""
        # Auto-seed system templates if table is empty
        self.seed_default_templates()

        definitions = (
            AutomationDefinition.query
            .filter(or_(AutomationDefinition.user_id == user_id, AutomationDefinition.is_template.is_(True)))
            .order_by(AutomationDefinition.is_template.desc(), AutomationDefinition.title.asc())
            .all()
        )
        return [d.to_dict() for d in definitions]

    def get_automation(self, automation_id: str, current_user_id: str) -> AutomationDefinition:
        """Fetch automation ensuring authorization or system template status."""
        item = AutomationDefinition.query.get(automation_id)
        if not item:
            raise NotFoundException("Automation definition not found")

        if not item.is_template:
            check_resource_ownership(item.user_id, current_user_id)

        return item

    def create_user_automation(
        self,
        user_id: str,
        title: str,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        category: str = "productivity",
        trigger_type: str = "manual",
        cron_expression: Optional[str] = None,
        scheduled_time: Optional[str] = None,
        scheduled_days: Optional[str] = None,
        configuration: Optional[Dict[str, Any]] = None
    ) -> AutomationDefinition:
        """Create a user-owned custom automation definition."""
        effective_slug = slug or title.lower().replace(" ", "_")[:64]

        # Prevent duplicate slug for same user
        existing = AutomationDefinition.query.filter_by(user_id=user_id, slug=effective_slug).first()
        if existing:
            raise ConflictException(f"An automation with identifier '{effective_slug}' already exists")

        definition = AutomationDefinition(
            user_id=user_id,
            slug=effective_slug,
            title=title,
            description=description,
            category=category,
            is_template=False,
            is_active=True,
            is_paused=False,
            trigger_type=trigger_type,
            cron_expression=cron_expression,
            scheduled_time=scheduled_time,
            scheduled_days=scheduled_days,
            configuration=configuration or {},
        )
        db.session.add(definition)
        db.session.commit()
        return definition

    def update_user_automation(
        self,
        automation_id: str,
        current_user_id: str,
        **kwargs
    ) -> AutomationDefinition:
        """Update an existing user automation definition."""
        item = self.get_automation(automation_id, current_user_id)
        if item.is_template:
            raise ForbiddenException("System automation templates cannot be directly modified. Create a custom copy.")

        for key, val in kwargs.items():
            if hasattr(item, key) and val is not None:
                setattr(item, key, val)

        db.session.commit()
        return item

    def delete_user_automation(self, automation_id: str, current_user_id: str) -> None:
        """Delete user automation definition."""
        item = self.get_automation(automation_id, current_user_id)
        if item.is_template:
            raise ForbiddenException("System templates cannot be deleted")

        db.session.delete(item)
        db.session.commit()

    # -------------------------------------------------------------------------
    # Execution Engine
    # -------------------------------------------------------------------------

    def execute_automation(
        self,
        automation_id: str,
        user_id: str,
        triggered_by: str = "manual",
        user_request: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> AutomationExecution:
        """Trigger an execution run through the automation workflow."""
        definition = self.get_automation(automation_id, user_id)

        if definition.is_paused:
            raise BadRequestException("Cannot execute a paused automation. Resume it first.")

        # Check idempotency if key provided
        if idempotency_key:
            existing = AutomationExecution.query.filter_by(
                user_id=user_id,
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing

        # Create execution record
        execution = AutomationExecution(
            user_id=user_id,
            definition_id=definition.id,
            idempotency_key=idempotency_key,
            triggered_by=triggered_by,
            status="planning",
            risk_level="low",
            trigger_payload={"user_request": user_request},
            started_at=datetime.now(timezone.utc),
        )
        db.session.add(execution)
        db.session.commit()

        start_time = time.perf_counter()

        initial_state = {
            "execution_id": execution.id,
            "user_id": user_id,
            "definition_slug": definition.slug,
            "user_request": user_request or f"Run automation: {definition.title}",
            "trigger_payload": execution.trigger_payload,
            "intent": "",
            "context_data": {},
            "formatted_context": "",
            "raw_plan": "",
            "proposed_actions": [],
            "validated_actions": [],
            "risk_level": "low",
            "requires_approval": False,
            "approvals_created": [],
            "executed_results": [],
            "verification_passed": False,
            "final_response": "",
            "error": None,
            "status": "planning",
        }

        try:
            result = lifeos_automation_graph.invoke(initial_state)

            execution.status = result.get("status", "completed")
            execution.risk_level = result.get("risk_level", "low")
            execution.summary = result.get("final_response", "")
            execution.completed_at = datetime.now(timezone.utc)
            execution.execution_duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Update definition stats
            definition.last_run_at = execution.completed_at
            definition.total_runs += 1
            if execution.status in ["completed", "awaiting_approval"]:
                definition.successful_runs += 1
            else:
                definition.failed_runs += 1

            db.session.commit()
            return execution

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc)
            execution.execution_duration_ms = int((time.perf_counter() - start_time) * 1000)
            definition.failed_runs += 1
            db.session.commit()
            return execution

    def get_execution(self, execution_id: str, current_user_id: str) -> AutomationExecution:
        """Retrieve execution with ownership check."""
        exec_item = AutomationExecution.query.get(execution_id)
        if not exec_item:
            raise NotFoundException("Automation execution not found")

        check_resource_ownership(exec_item.user_id, current_user_id)
        return exec_item

    def list_executions(
        self,
        user_id: str,
        definition_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List execution history for authenticated user."""
        query = AutomationExecution.query.filter_by(user_id=user_id)
        if definition_id:
            query = query.filter_by(definition_id=definition_id)
        if status:
            query = query.filter_by(status=status)

        items = query.order_by(desc(AutomationExecution.created_at)).offset(offset).limit(limit).all()
        return [item.to_dict(include_children=False) for item in items]

    # -------------------------------------------------------------------------
    # Approval Flow
    # -------------------------------------------------------------------------

    def get_approval(self, approval_id: str, current_user_id: str) -> AutomationApproval:
        """Fetch approval record with ownership verification."""
        appr = AutomationApproval.query.get(approval_id)
        if not appr:
            raise NotFoundException("Approval record not found")

        check_resource_ownership(appr.user_id, current_user_id)
        return appr

    def approve_action(self, approval_id: str, current_user_id: str) -> Dict[str, Any]:
        """Approve proposed action, revalidate parameter hash, and execute via tool registry."""
        approval = self.get_approval(approval_id, current_user_id)

        if approval.status != "pending":
            raise BadRequestException(f"Approval cannot be approved in '{approval.status}' status")

        if approval.is_expired:
            approval.status = "expired"
            db.session.commit()
            raise BadRequestException("This approval request has expired and cannot be executed.")

        action = approval.action
        if not action:
            raise NotFoundException("Linked action not found")

        # Cryptographic parameter re-verification
        param_json = json.dumps(action.parameters, sort_keys=True)
        param_hash = hashlib.sha256(param_json.encode("utf-8")).hexdigest()
        if param_hash != approval.parameter_hash:
            raise BadRequestException("Proposed parameters have mutated since approval generation.")

        # Re-verify resource ownership and execute tool
        try:
            result = automation_tool_registry.execute_tool(
                action.tool_name,
                current_user_id,
                action.parameters
            )
            action.status = "executed"
            action.result_payload = result
            approval.status = "approved"
            approval.responded_at = datetime.now(timezone.utc)

            # Check if all actions in this execution are resolved
            exec_record = approval.execution
            all_resolved = all(
                a.status in ["executed", "rejected", "failed"]
                for a in exec_record.actions
            )
            if all_resolved:
                exec_record.status = "completed"

            db.session.commit()
            return {
                "approval_id": approval.id,
                "status": "approved",
                "action_status": action.status,
                "result": result
            }
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            db.session.commit()
            raise BadRequestException(f"Failed to execute approved action: {str(e)}")

    def reject_action(self, approval_id: str, current_user_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Reject proposed action and update execution state."""
        approval = self.get_approval(approval_id, current_user_id)

        if approval.status != "pending":
            raise BadRequestException(f"Approval cannot be rejected in '{approval.status}' status")

        approval.status = "rejected"
        approval.responded_at = datetime.now(timezone.utc)
        approval.decision_reason = reason

        action = approval.action
        if action:
            action.status = "rejected"

        # Update execution status
        exec_record = approval.execution
        all_resolved = all(
            a.status in ["executed", "rejected", "failed"]
            for a in exec_record.actions
        )
        if all_resolved:
            exec_record.status = "completed"

        db.session.commit()
        return {
            "approval_id": approval.id,
            "status": "rejected",
            "decision_reason": reason
        }

    # -------------------------------------------------------------------------
    # Operational Controls: Cancel, Pause, Resume
    # -------------------------------------------------------------------------

    def cancel_execution(self, execution_id: str, current_user_id: str) -> Dict[str, Any]:
        """Cancel an in-flight, awaiting-approval, or completed execution."""
        exec_record = self.get_execution(execution_id, current_user_id)

        if exec_record.status == "cancelled":
            raise BadRequestException("Execution is already cancelled")

        exec_record.status = "cancelled"
        exec_record.completed_at = datetime.now(timezone.utc)

        # Cancel any pending approvals
        for appr in exec_record.approvals:
            if appr.status == "pending":
                appr.status = "cancelled"
        for act in exec_record.actions:
            if act.status in ["pending", "awaiting_approval"]:
                act.status = "skipped"

        db.session.commit()
        return {"execution_id": exec_record.id, "status": "cancelled"}

    def pause_automation(self, automation_id: str, current_user_id: str) -> Dict[str, Any]:
        """Pause a scheduled automation definition."""
        item = self.get_automation(automation_id, current_user_id)
        item.is_paused = True
        db.session.commit()
        return {"automation_id": item.id, "is_paused": True}

    def resume_automation(self, automation_id: str, current_user_id: str) -> Dict[str, Any]:
        """Resume a paused automation definition."""
        item = self.get_automation(automation_id, current_user_id)
        item.is_paused = False
        db.session.commit()
        return {"automation_id": item.id, "is_paused": False}

    # -------------------------------------------------------------------------
    # Scheduler Engine Integration
    # -------------------------------------------------------------------------

    def run_scheduled_automations(self) -> int:
        """Background hook to evaluate active scheduled automations for all users.
        Respects user timezone, avoids duplicate execution via idempotency, and records stats.
        """
        now_utc = datetime.now(timezone.utc)
        current_day_name = now_utc.strftime("%A").lower()
        is_weekday = now_utc.weekday() < 5

        # Query all active, non-paused automations with trigger_type='scheduled'
        active_sched = AutomationDefinition.query.filter(
            AutomationDefinition.is_active.is_(True),
            AutomationDefinition.is_paused.is_(False),
            AutomationDefinition.trigger_type == "scheduled"
        ).all()

        executed_count = 0

        # Fetch users
        users = User.query.all()
        user_map = {u.id: u for u in users}

        for definition in active_sched:
            # Check match against days
            sched_days = (definition.scheduled_days or "daily").lower()
            if sched_days == "weekdays" and not is_weekday:
                continue
            if sched_days in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                if sched_days != current_day_name:
                    continue

            # Determine target user(s)
            target_user_ids = [definition.user_id] if definition.user_id else [u.id for u in users]

            for uid in target_user_ids:
                if not uid:
                    continue

                # Formulate daily idempotency key
                today_str = now_utc.strftime("%Y-%m-%d")
                idemp_key = f"scheduled:{definition.slug}:{uid}:{today_str}"

                # Check if already executed today
                already_ran = AutomationExecution.query.filter_by(
                    user_id=uid,
                    idempotency_key=idemp_key
                ).first()
                if already_ran:
                    continue

                try:
                    self.execute_automation(
                        automation_id=definition.id,
                        user_id=uid,
                        triggered_by="scheduled",
                        idempotency_key=idemp_key
                    )
                    executed_count += 1
                except Exception:
                    # Never let one user failure abort the loop
                    pass

        return executed_count
