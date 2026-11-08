"""LifeOS - Controlled Automation Tool Registry.

Enforces strict input validation, permission boundaries, and ownership checks.
Every tool operates as a controlled function returning structured JSON.
Arbitrary code execution or direct SQL access is prohibited.
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, date, timezone, timedelta
from pydantic import BaseModel, Field, ValidationError

from app.models.task import Task
from app.models.planner import PlannerBlock
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal, GoalMilestone
from app.models.finance import FinancialTransaction, Budget, SavingsGoal, FinancialCategory
from app.models.notification import Reminder
from app.services.task_service import TaskService
from app.services.planner_service import PlannerService
from app.services.notification_service import NotificationService
from app.core.security import check_resource_ownership
from app import db


# -----------------------------------------------------------------------------
# Pydantic Tool Input Validation Schemas
# -----------------------------------------------------------------------------

class CreateTaskSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    category_id: Optional[str] = None
    due_date: Optional[str] = None  # ISO format string
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)


class UpdateTaskSchema(BaseModel):
    task_id: str
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    due_date: Optional[str] = None


class GetPendingTasksSchema(BaseModel):
    limit: int = Field(10, ge=1, le=50)


class CreatePlannerBlockSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    start_time: str  # ISO string
    end_time: str    # ISO string
    block_type: str = Field("task", pattern="^(task|deep_work|meeting|break|routine)$")
    description: Optional[str] = Field(None, max_length=500)
    task_id: Optional[str] = None


class GetUpcomingScheduleSchema(BaseModel):
    days_ahead: int = Field(1, ge=1, le=7)


class CreateReminderSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    reminder_time: str  # ISO string
    description: Optional[str] = Field(None, max_length=255)
    entity_type: Optional[str] = Field("general", pattern="^(general|task|habit|goal|planner)$")
    entity_id: Optional[str] = None


class ReadOnlyFinanceSchema(BaseModel):
    month: Optional[str] = None  # YYYY-MM


# -----------------------------------------------------------------------------
# Tool Execution Registry
# -----------------------------------------------------------------------------

class ToolDefinition:
    """Metadata and execution container for a registered automation tool."""

    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        risk_level: str,  # low, medium, high
        requires_approval: bool,
        schema_cls: Optional[type] = None,
        handler: Optional[Callable] = None
    ):
        self.name = name
        self.category = category
        self.description = description
        self.risk_level = risk_level
        self.requires_approval = requires_approval
        self.schema_cls = schema_cls
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "risk_level": self.risk_level,
            "requires_approval": self.requires_approval,
        }


class AutomationToolRegistry:
    """Central registry of strictly approved tools callable by automation workflows."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._tools.values()]

    def execute_tool(
        self,
        tool_name: str,
        user_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate input parameters against schema, enforce user boundaries, and execute."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Unauthorized or unknown tool: '{tool_name}'")

        # Validate with Pydantic schema if defined
        validated_params = parameters
        if tool.schema_cls:
            try:
                validated_model = tool.schema_cls(**(parameters or {}))
                validated_params = validated_model.model_dump()
            except ValidationError as e:
                raise ValueError(f"Tool parameter validation error: {str(e)}")

        # Execute handler strictly scoped to user_id
        return tool.handler(user_id=user_id, **validated_params)

    # -------------------------------------------------------------------------
    # Default Registered Tools
    # -------------------------------------------------------------------------

    def _register_default_tools(self) -> None:
        # === TASKS ===
        self.register(ToolDefinition(
            name="tasks.create_task",
            category="tasks",
            description="Create a new task in the user's task repository.",
            risk_level="medium",
            requires_approval=True,
            schema_cls=CreateTaskSchema,
            handler=self._tool_create_task
        ))
        self.register(ToolDefinition(
            name="tasks.update_task",
            category="tasks",
            description="Update an existing task status, priority, or due date.",
            risk_level="high",
            requires_approval=True,
            schema_cls=UpdateTaskSchema,
            handler=self._tool_update_task
        ))
        self.register(ToolDefinition(
            name="tasks.get_pending_tasks",
            category="tasks",
            description="Retrieve active pending and in-progress tasks.",
            risk_level="low",
            requires_approval=False,
            schema_cls=GetPendingTasksSchema,
            handler=self._tool_get_pending_tasks
        ))

        # === PLANNER ===
        self.register(ToolDefinition(
            name="planner.create_block",
            category="planner",
            description="Schedule a dedicated time block in the user's daily planner.",
            risk_level="medium",
            requires_approval=True,
            schema_cls=CreatePlannerBlockSchema,
            handler=self._tool_create_planner_block
        ))
        self.register(ToolDefinition(
            name="planner.get_upcoming_schedule",
            category="planner",
            description="Retrieve planned calendar blocks for today and upcoming days.",
            risk_level="low",
            requires_approval=False,
            schema_cls=GetUpcomingScheduleSchema,
            handler=self._tool_get_upcoming_schedule
        ))

        # === HABITS ===
        self.register(ToolDefinition(
            name="habits.get_habit_progress",
            category="habits",
            description="Retrieve current active habits, check-ins, and streak metrics.",
            risk_level="low",
            requires_approval=False,
            schema_cls=None,
            handler=self._tool_get_habit_progress
        ))

        # === GOALS ===
        self.register(ToolDefinition(
            name="goals.get_goal_progress",
            category="goals",
            description="Retrieve user goals and milestone completion percentages.",
            risk_level="low",
            requires_approval=False,
            schema_cls=None,
            handler=self._tool_get_goal_progress
        ))

        # === NOTIFICATIONS & REMINDERS ===
        self.register(ToolDefinition(
            name="notifications.create_reminder",
            category="notifications",
            description="Schedule an in-app reminder notification at a designated time.",
            risk_level="medium",
            requires_approval=True,
            schema_cls=CreateReminderSchema,
            handler=self._tool_create_reminder
        ))
        self.register(ToolDefinition(
            name="notifications.get_upcoming_reminders",
            category="notifications",
            description="Retrieve scheduled reminders for the authenticated user.",
            risk_level="low",
            requires_approval=False,
            schema_cls=None,
            handler=self._tool_get_upcoming_reminders
        ))

        # === FINANCE (STRICT READ-ONLY AGGREGATES) ===
        self.register(ToolDefinition(
            name="finance.get_financial_summary",
            category="finance",
            description="Read verified monthly income, expense totals, and budget adherence (strictly read-only).",
            risk_level="low",
            requires_approval=False,
            schema_cls=ReadOnlyFinanceSchema,
            handler=self._tool_get_financial_summary
        ))

    # -------------------------------------------------------------------------
    # Tool Handler Implementations (Strict Ownership Checked)
    # -------------------------------------------------------------------------

    def _tool_create_task(self, user_id: str, title: str, description: Optional[str] = None,
                          priority: str = "medium", category_id: Optional[str] = None,
                          due_date: Optional[str] = None, estimated_minutes: Optional[int] = None) -> Dict[str, Any]:
        task_service = TaskService()
        parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00")) if due_date else None
        task = task_service.create_task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category_id=category_id,
            due_date=parsed_due,
            estimated_minutes=estimated_minutes
        )
        return {
            "task_id": task.id,
            "title": task.title,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
        }

    def _tool_update_task(self, user_id: str, task_id: str, title: Optional[str] = None,
                          status: Optional[str] = None, priority: Optional[str] = None,
                          due_date: Optional[str] = None) -> Dict[str, Any]:
        task_service = TaskService()
        parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00")) if due_date else None
        task = task_service.update_task(
            task_id=task_id,
            current_user_id=user_id,
            title=title,
            status=status,
            priority=priority,
            due_date=parsed_due
        )
        return {
            "task_id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
        }

    def _tool_get_pending_tasks(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        tasks = (
            Task.query
            .filter(Task.user_id == user_id, Task.status.in_(["pending", "in_progress"]))
            .order_by(Task.due_date.asc().nulls_last(), Task.priority.desc())
            .limit(limit)
            .all()
        )
        return {
            "count": len(tasks),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority,
                    "status": t.status,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "estimated_minutes": t.estimated_minutes
                }
                for t in tasks
            ]
        }

    def _tool_create_planner_block(self, user_id: str, title: str, start_time: str, end_time: str,
                                   block_type: str = "task", description: Optional[str] = None,
                                   task_id: Optional[str] = None) -> Dict[str, Any]:
        planner_service = PlannerService()
        parsed_start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        parsed_end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        block = planner_service.create_block(
            user_id=user_id,
            title=title,
            start_time=parsed_start,
            end_time=parsed_end,
            description=description,
            block_type=block_type,
            task_id=task_id
        )
        return {
            "block_id": block.id,
            "title": block.title,
            "block_type": block.block_type,
            "start_time": block.start_time.isoformat(),
            "end_time": block.end_time.isoformat(),
            "status": block.status,
        }

    def _tool_get_upcoming_schedule(self, user_id: str, days_ahead: int = 1) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        start_of_day = datetime(now_utc.year, now_utc.month, now_utc.day, 0, 0, 0, tzinfo=timezone.utc)
        end_window = start_of_day + timedelta(days=days_ahead)

        blocks = (
            PlannerBlock.query
            .filter(
                PlannerBlock.user_id == user_id,
                PlannerBlock.start_time >= start_of_day,
                PlannerBlock.start_time <= end_window,
                PlannerBlock.status != "cancelled"
            )
            .order_by(PlannerBlock.start_time.asc())
            .all()
        )
        return {
            "count": len(blocks),
            "blocks": [
                {
                    "id": b.id,
                    "title": b.title,
                    "block_type": b.block_type,
                    "start_time": b.start_time.isoformat(),
                    "end_time": b.end_time.isoformat(),
                    "status": b.status,
                }
                for b in blocks
            ]
        }

    def _tool_get_habit_progress(self, user_id: str, **kwargs) -> Dict[str, Any]:
        today = date.today()
        habits = Habit.query.filter_by(user_id=user_id, is_archived=False).all()
        habit_ids = [h.id for h in habits]
        today_logs = {}
        if habit_ids:
            logs = HabitLog.query.filter(HabitLog.habit_id.in_(habit_ids), HabitLog.log_date == today).all()
            today_logs = {l.habit_id: l.completed for l in logs}

        return {
            "total_habits": len(habits),
            "habits": [
                {
                    "id": h.id,
                    "title": h.title,
                    "frequency": h.frequency,
                    "current_streak": h.current_streak,
                    "completed_today": today_logs.get(h.id, False),
                }
                for h in habits
            ]
        }

    def _tool_get_goal_progress(self, user_id: str, **kwargs) -> Dict[str, Any]:
        goals = (
            Goal.query
            .filter(Goal.user_id == user_id, Goal.status.in_(["in_progress", "active", "not_started"]))
            .order_by(Goal.target_date.asc().nulls_last())
            .all()
        )
        return {
            "total_goals": len(goals),
            "goals": [
                {
                    "id": g.id,
                    "title": g.title,
                    "progress_percent": g.progress_percent,
                    "status": g.status,
                    "priority": g.priority,
                    "target_date": g.target_date.isoformat() if g.target_date else None,
                    "milestones_count": len(g.milestones) if g.milestones else 0,
                    "completed_milestones": sum(1 for m in g.milestones if m.is_completed) if g.milestones else 0,
                }
                for g in goals
            ]
        }

    def _tool_create_reminder(self, user_id: str, title: str, reminder_time: str,
                              description: Optional[str] = None, entity_type: Optional[str] = "general",
                              entity_id: Optional[str] = None) -> Dict[str, Any]:
        notif_service = NotificationService()
        parsed_time = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))
        reminder = notif_service.repo.create_reminder(
            user_id=user_id,
            title=title,
            reminder_time=parsed_time,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id
        )
        return {
            "reminder_id": reminder.id,
            "title": reminder.title,
            "reminder_time": reminder.reminder_time.isoformat(),
            "status": reminder.status,
        }

    def _tool_get_upcoming_reminders(self, user_id: str, **kwargs) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        reminders = (
            Reminder.query
            .filter(Reminder.user_id == user_id, Reminder.status == "pending", Reminder.reminder_time >= now_utc)
            .order_by(Reminder.reminder_time.asc())
            .limit(10)
            .all()
        )
        return {
            "count": len(reminders),
            "reminders": [
                {
                    "id": r.id,
                    "title": r.title,
                    "reminder_time": r.reminder_time.isoformat(),
                    "description": r.description
                }
                for r in reminders
            ]
        }

    def _tool_get_financial_summary(self, user_id: str, month: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Strictly read-only aggregate query of verified financial records."""
        from decimal import Decimal
        target_month = month or datetime.now(timezone.utc).strftime("%Y-%m")

        start_dt = datetime.strptime(f"{target_month}-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if start_dt.month == 12:
            end_dt = datetime(start_dt.year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
        else:
            end_dt = datetime(start_dt.year, start_dt.month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

        txs = FinancialTransaction.query.filter(
            FinancialTransaction.user_id == user_id,
            FinancialTransaction.is_deleted.is_(False),
            FinancialTransaction.transaction_date.between(start_dt, end_dt)
        ).all()

        income = sum((t.amount for t in txs if t.transaction_type == "income"), start=Decimal("0.00"))
        expense = sum((t.amount for t in txs if t.transaction_type == "expense"), start=Decimal("0.00"))
        net_savings = income - expense

        budgets = Budget.query.filter_by(user_id=user_id, month=target_month).all()
        total_budget = sum((b.amount for b in budgets), start=Decimal("0.00"))

        return {
            "month": target_month,
            "total_income": str(income),
            "total_expenses": str(expense),
            "net_savings": str(net_savings),
            "total_budget": str(total_budget),
            "transaction_count": len(txs),
            "notice": "Verified read-only ledger aggregates. AI is prohibited from modifying financial transactions."
        }


# Global tool registry singleton
automation_tool_registry = AutomationToolRegistry()
