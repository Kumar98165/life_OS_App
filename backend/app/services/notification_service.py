import json
import hashlib
from datetime import datetime, timezone, timedelta, time
from typing import Optional, List, Dict, Any, Tuple
from zoneinfo import ZoneInfo
import httpx
from app import db
from app.models.notification import (
    Notification,
    NotificationPreference,
    Reminder,
    PushDeviceToken,
    NotificationDelivery,
)
from app.repositories.notification_repository import NotificationRepository
from app.models.task import Task
from app.models.planner import PlannerBlock
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal
from app.models.finance import Budget, SavingsGoal


class NotificationService:
    """Centralized LifeOS notification, reminder scheduling, and delivery engine."""

    def __init__(self, repo: Optional[NotificationRepository] = None):
        self.repo = repo or NotificationRepository()

    # -------------------------------------------------------------------------
    # Preference & Quiet Hours Evaluation
    # -------------------------------------------------------------------------

    def is_in_quiet_hours(self, pref: NotificationPreference, now_utc: Optional[datetime] = None) -> bool:
        """Evaluate if user is currently inside their configured quiet hours window."""
        if not pref.quiet_hours_enabled:
            return False

        if not now_utc:
            now_utc = datetime.now(timezone.utc)

        try:
            user_tz = ZoneInfo(pref.timezone or "UTC")
        except Exception:
            user_tz = timezone.utc

        local_dt = now_utc.astimezone(user_tz)
        current_time = local_dt.time()

        start_h, start_m = map(int, pref.quiet_hours_start.split(":"))
        end_h, end_m = map(int, pref.quiet_hours_end.split(":"))

        start_time = time(start_h, start_m)
        end_time = time(end_h, end_m)

        if start_time < end_time:
            # Daytime interval (e.g. 13:00 to 15:00)
            return start_time <= current_time < end_time
        else:
            # Overnight interval (e.g. 22:00 to 08:00)
            return current_time >= start_time or current_time < end_time

    def is_category_enabled(self, pref: NotificationPreference, category: str) -> bool:
        """Check if notification category is enabled in user settings."""
        cat_lower = (category or "").lower()
        if cat_lower in ["task", "tasks"]:
            return pref.tasks_enabled
        elif cat_lower in ["planner", "calendar"]:
            return pref.planner_enabled
        elif cat_lower in ["habit", "habits"]:
            return pref.habits_enabled
        elif cat_lower in ["goal", "goals"]:
            return pref.goals_enabled
        elif cat_lower in ["finance", "budget", "savings"]:
            return pref.finance_enabled
        return True

    # -------------------------------------------------------------------------
    # Core Dispatcher & Deduplication
    # -------------------------------------------------------------------------

    def create_and_dispatch(
        self,
        user_id: str,
        title: str,
        body: str,
        notification_type: str = "general",
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        data_payload: Optional[Dict[str, Any]] = None,
        dedup_key: Optional[str] = None,
        scheduled_for: Optional[datetime] = None,
    ) -> Optional[Notification]:
        """Validate preferences, quiet hours, and dispatch notification across in-app & push."""
        pref = self.repo.get_or_create_preferences(user_id)

        # 1. Category filter
        if not self.is_category_enabled(pref, notification_type):
            return None

        # 2. In-app toggle filter
        if not pref.in_app_enabled:
            return None

        # 3. Deduplication hash
        dedup_hash = None
        if dedup_key:
            dedup_hash = hashlib.sha256(f"{user_id}:{dedup_key}".encode("utf-8")).hexdigest()

        payload_str = json.dumps(data_payload) if data_payload else None

        notif = self.repo.create_notification(
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type,
            entity_type=entity_type,
            entity_id=entity_id,
            scheduled_for=scheduled_for,
            data_payload=payload_str,
            dedup_hash=dedup_hash,
            is_delivered=True,
        )

        if not notif:
            return None

        # Log in-app delivery
        self.repo.log_delivery(
            notification_id=notif.id,
            channel="in_app",
            status="delivered",
        )

        # 4. Optional Push Notification Dispatch
        if pref.push_enabled:
            if self.is_in_quiet_hours(pref):
                self.repo.log_delivery(
                    notification_id=notif.id,
                    channel="expo_push",
                    status="skipped_quiet_hours",
                    error_message="Push suppressed during active quiet hours",
                )
            else:
                self._dispatch_push_tokens(notif, user_id, data_payload)

        return notif

    def _dispatch_push_tokens(
        self,
        notification: Notification,
        user_id: str,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send push notification to registered Expo push tokens for user."""
        tokens = self.repo.list_active_device_tokens(user_id)
        if not tokens:
            return

        messages = []
        for dev in tokens:
            messages.append({
                "to": dev.token,
                "sound": "default",
                "title": notification.title,
                "body": notification.body,
                "data": data_payload or {},
            })

        # Send via Expo HTTP Push endpoint
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.post(
                    "https://exp.host/--/api/v2/push/send",
                    json=messages,
                    headers={"Accept": "application/json", "Accept-Encoding": "gzip, deflate"}
                )
                if resp.status_code == 200:
                    for dev in tokens:
                        self.repo.log_delivery(
                            notification_id=notification.id,
                            channel="expo_push",
                            status="delivered",
                            device_token_id=dev.id
                        )
                else:
                    for dev in tokens:
                        self.repo.log_delivery(
                            notification_id=notification.id,
                            channel="expo_push",
                            status="failed",
                            error_message=f"HTTP {resp.status_code}: {resp.text}",
                            device_token_id=dev.id
                        )
        except Exception as e:
            # Graceful network/timeout handling - does not disrupt database or in-app notif
            for dev in tokens:
                self.repo.log_delivery(
                    notification_id=notification.id,
                    channel="expo_push",
                    status="failed",
                    error_message=str(e),
                    device_token_id=dev.id
                )

    # -------------------------------------------------------------------------
    # Contextual Verified Application Scanners
    # -------------------------------------------------------------------------

    def check_task_reminders(self, user_id: str) -> List[Notification]:
        """Scan user tasks for upcoming due dates (due today) and overdue items."""
        now = datetime.now(timezone.utc)
        today_date = now.date()

        tasks = list(
            db.session.execute(
                db.select(Task).where(
                    Task.user_id == user_id,
                    Task.status != "completed",
                    Task.due_date.is_not(None)
                )
            ).scalars().all()
        )

        generated = []
        for t in tasks:
            task_due_date = t.due_date.date() if t.due_date else None
            if not task_due_date:
                continue

            if task_due_date < today_date:
                # Overdue
                notif = self.create_and_dispatch(
                    user_id=user_id,
                    title=f"Task Overdue: {t.title}",
                    body=f"This task was due on {task_due_date.isoformat()}. Complete or reschedule it.",
                    notification_type="task",
                    entity_type="task",
                    entity_id=t.id,
                    data_payload={"route": "TasksTab", "taskId": t.id},
                    dedup_key=f"task_overdue:{t.id}:{today_date.isoformat()}"
                )
                if notif:
                    generated.append(notif)
            elif task_due_date == today_date:
                # Due today
                notif = self.create_and_dispatch(
                    user_id=user_id,
                    title=f"Task Due Today: {t.title}",
                    body="Scheduled for today. Stay focused on your priority goals.",
                    notification_type="task",
                    entity_type="task",
                    entity_id=t.id,
                    data_payload={"route": "TasksTab", "taskId": t.id},
                    dedup_key=f"task_due_today:{t.id}:{today_date.isoformat()}"
                )
                if notif:
                    generated.append(notif)

        return generated

    def check_habit_reminders(self, user_id: str) -> List[Notification]:
        """Check active habits that have not been checked in today."""
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")

        habits = list(
            db.session.execute(
                db.select(Habit).where(
                    Habit.user_id == user_id,
                    Habit.is_archived.is_(False)
                )
            ).scalars().all()
        )

        # Check logs for today
        logs = list(
            db.session.execute(
                db.select(HabitLog).where(
                    HabitLog.user_id == user_id,
                    HabitLog.log_date == now.date()
                )
            ).scalars().all()
        )
        completed_habit_ids = {l.habit_id for l in logs if l.completed}

        generated = []
        for h in habits:
            if h.id not in completed_habit_ids:
                notif = self.create_and_dispatch(
                    user_id=user_id,
                    title=f"Daily Habit: {h.title}",
                    body=f"Don't break your streak! Remember to check in for {h.title} today.",
                    notification_type="habit",
                    entity_type="habit",
                    entity_id=h.id,
                    data_payload={"route": "Habits", "habitId": h.id},
                    dedup_key=f"habit_daily:{h.id}:{today_str}"
                )
                if notif:
                    generated.append(notif)

        return generated

    def check_finance_alerts(self, user_id: str) -> List[Notification]:
        """Check active monthly budgets for threshold overruns (>= 80% or 100%)."""
        now = datetime.now(timezone.utc)
        current_month = now.strftime("%Y-%m")

        budgets = list(
            db.session.execute(
                db.select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.month == current_month
                )
            ).scalars().all()
        )

        generated = []
        for b in budgets:
            # Live calculate spent
            cat_name = b.category.name if b.category else "Overall"
            # If over budget, notify
            from app.services.finance_service import FinanceService
            fsvc = FinanceService()
            budgets_with_util = fsvc.list_budgets_with_utilization(user_id, current_month)
            for b_util in budgets_with_util:
                if b_util["id"] == b.id:
                    pct = b_util.get("utilization_percentage", 0)
                    if b_util.get("is_over_budget"):
                        notif = self.create_and_dispatch(
                            user_id=user_id,
                            title=f"Budget Exceeded: {cat_name}",
                            body=f"You have spent ${b_util['spent_amount']} of your ${b.amount} monthly budget ({pct}%).",
                            notification_type="finance",
                            entity_type="budget",
                            entity_id=b.id,
                            data_payload={"route": "BudgetManagement", "budgetId": b.id},
                            dedup_key=f"budget_over:{b.id}:{current_month}"
                        )
                        if notif:
                            generated.append(notif)
                    elif pct >= 80.0:
                        notif = self.create_and_dispatch(
                            user_id=user_id,
                            title=f"Budget Warning: {cat_name}",
                            body=f"You have reached {pct}% of your ${b.amount} monthly limit.",
                            notification_type="finance",
                            entity_type="budget",
                            entity_id=b.id,
                            data_payload={"route": "BudgetManagement", "budgetId": b.id},
                            dedup_key=f"budget_warning_80:{b.id}:{current_month}"
                        )
                        if notif:
                            generated.append(notif)
        return generated

    # -------------------------------------------------------------------------
    # Reminder Scheduler Engine
    # -------------------------------------------------------------------------

    def process_due_reminders(self, current_time: Optional[datetime] = None) -> int:
        """Fetch and execute all due reminders atomically and idempotently."""
        if not current_time:
            current_time = datetime.now(timezone.utc)

        due_reminders = self.repo.get_due_reminders(current_time=current_time, limit=100)
        processed_count = 0

        for r in due_reminders:
            try:
                # 1. Create notification
                notif = self.create_and_dispatch(
                    user_id=r.user_id,
                    title=f"Reminder: {r.title}",
                    body=r.description or "You have a scheduled reminder.",
                    notification_type="reminder",
                    entity_type=r.entity_type or "reminder",
                    entity_id=r.entity_id or r.id,
                    data_payload={"route": "ReminderManagement", "reminderId": r.id},
                    dedup_key=f"reminder:{r.id}:{r.reminder_time.isoformat()}"
                )

                # 2. Mark reminder as triggered
                r.status = "triggered"
                r.triggered_at = datetime.now(timezone.utc)
                if notif:
                    r.notification_id = notif.id

                # 3. Handle recurrence
                if r.is_recurring and r.recurrence_rule:
                    next_time = self._compute_next_reminder_time(r.reminder_time, r.recurrence_rule)
                    if next_time:
                        self.repo.create_reminder(
                            user_id=r.user_id,
                            title=r.title,
                            reminder_time=next_time,
                            description=r.description,
                            entity_type=r.entity_type,
                            entity_id=r.entity_id,
                            is_recurring=True,
                            recurrence_rule=r.recurrence_rule,
                        )

                db.session.commit()
                processed_count += 1
            except Exception as e:
                db.session.rollback()

        return processed_count

    def _compute_next_reminder_time(self, base_time: datetime, rule: str) -> Optional[datetime]:
        """Compute the next occurrence timestamp according to recurrence rule."""
        if base_time.tzinfo is None:
            base_time = base_time.replace(tzinfo=timezone.utc)
        rule_lower = rule.lower()
        if rule_lower == "daily":
            return base_time + timedelta(days=1)
        elif rule_lower == "weekdays":
            next_t = base_time + timedelta(days=1)
            while next_t.weekday() >= 5:  # Saturday or Sunday
                next_t += timedelta(days=1)
            return next_t
        elif rule_lower == "weekly":
            return base_time + timedelta(weeks=1)
        elif rule_lower == "monthly":
            # Add 30 days
            return base_time + timedelta(days=30)
        return None

