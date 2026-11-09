"""LifeOS - Safe Read-Only Agent Tools.

Controlled tools providing authenticated, user-scoped access to Tasks,
Goals, Habits, and Planner blocks without modifying user data.
"""
from datetime import date, datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo
from sqlalchemy import or_, and_
from sqlalchemy.orm import selectinload
from app.models.task import Task
from app.models.goal import Goal
from app.models.habit import Habit, HabitLog
from app.models.planner import PlannerBlock
from app.models.finance import FinancialAccount, FinancialTransaction


def get_pending_tasks(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve up to limit pending or in-progress tasks for user."""
    tasks = (
        Task.query
        .filter(Task.user_id == user_id, Task.status.in_(["pending", "in_progress", "todo"]))
        .order_by(Task.due_date.asc().nulls_last(), Task.priority.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        }
        for t in tasks
    ]


def get_today_tasks(user_id: str, limit: int = 10, target_date: Optional[date] = None, tz_name: str = "UTC") -> List[Dict[str, Any]]:
    """Retrieve tasks due on target date (or today in user's timezone) for user."""
    try:
        user_tz = ZoneInfo(tz_name)
    except Exception:
        user_tz = timezone.utc

    if not target_date:
        target_date = datetime.now(user_tz).date()

    # Convert user's local start of day and end of day to UTC for accurate database querying
    start_local = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=user_tz)
    end_local = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=user_tz)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    tasks = (
        Task.query
        .filter(
            Task.user_id == user_id,
            Task.due_date >= start_utc,
            Task.due_date <= end_utc
        )
        .order_by(Task.status.asc(), Task.priority.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "completed": t.status == "completed",
        }
        for t in tasks
    ]


def get_approaching_deadlines(user_id: str, days_ahead: int = 3, limit: int = 5, tz_name: str = "UTC") -> List[Dict[str, Any]]:
    """Retrieve tasks due within the upcoming days_ahead window that are not yet completed."""
    try:
        tz = ZoneInfo(tz_name)
        now_dt = datetime.now(tz)
    except Exception:
        now_dt = datetime.now(timezone.utc)

    now_utc = now_dt.astimezone(timezone.utc)
    future_utc = now_utc + timedelta(days=days_ahead)

    tasks = (
        Task.query
        .filter(
            Task.user_id == user_id,
            Task.status.in_(["todo", "pending", "in_progress"]),
            Task.due_date >= now_utc,
            Task.due_date <= future_utc
        )
        .order_by(Task.due_date.asc(), Task.priority.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        }
        for t in tasks
    ]


def get_active_goals(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve active user goals with milestone completion progress."""
    goals = (
        Goal.query
        .options(selectinload(Goal.milestones))
        .filter(
            Goal.user_id == user_id,
            Goal.status.in_(["in_progress", "active", "not_started"])
        )
        .order_by(Goal.target_date.asc().nulls_last())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": g.id,
            "title": g.title,
            "priority": g.priority,
            "status": g.status,
            "progress_percent": g.progress_percent,
            "target_date": g.target_date.isoformat() if g.target_date else None,
            "total_milestones": len(g.milestones) if g.milestones else 0,
            "completed_milestones": sum(1 for m in g.milestones if m.is_completed) if g.milestones else 0,
        }
        for g in goals
    ]


def get_today_habits(user_id: str, target_date: Optional[date] = None, tz_name: str = "UTC") -> List[Dict[str, Any]]:
    """Retrieve active habits and check-in status for the target date."""
    if not target_date:
        try:
            tz = ZoneInfo(tz_name)
            target_date = datetime.now(tz).date()
        except Exception:
            target_date = date.today()

    habits = (
        Habit.query
        .filter(Habit.user_id == user_id, Habit.is_archived.is_(False))
        .order_by(Habit.created_at.desc())
        .all()
    )

    habit_ids = [h.id for h in habits]
    today_logs = {}
    yesterday_logs = {}
    yesterday = target_date - timedelta(days=1)

    if habit_ids:
        logs = (
            HabitLog.query
            .filter(
                HabitLog.habit_id.in_(habit_ids),
                HabitLog.log_date.in_([target_date, yesterday])
            )
            .all()
        )
        for l in logs:
            if l.log_date == target_date:
                today_logs[l.habit_id] = l.completed
            elif l.log_date == yesterday:
                yesterday_logs[l.habit_id] = l.completed

    is_weekday = target_date.weekday() < 5
    result = []
    for h in habits:
        is_scheduled = True
        if h.frequency == "weekdays" and not is_weekday:
            is_scheduled = False

        result.append({
            "id": h.id,
            "title": h.title,
            "frequency": h.frequency,
            "current_streak": h.current_streak,
            "completed_today": today_logs.get(h.id, False),
            "completed_yesterday": yesterday_logs.get(h.id, False),
            "is_scheduled": is_scheduled,
        })
    return result


def get_today_schedule(user_id: str, target_date: Optional[date] = None, tz_name: str = "UTC") -> List[Dict[str, Any]]:
    """Retrieve target date planner blocks in chronological order and detect overlaps."""
    try:
        user_tz = ZoneInfo(tz_name)
    except Exception:
        user_tz = timezone.utc

    if not target_date:
        target_date = datetime.now(user_tz).date()

    # Convert user's local start of day and end of day to UTC for accurate database querying
    start_local = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=user_tz)
    end_local = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=user_tz)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    blocks = (
        PlannerBlock.query
        .filter(
            PlannerBlock.user_id == user_id,
            PlannerBlock.start_time >= start_utc,
            PlannerBlock.start_time <= end_utc
        )
        .order_by(PlannerBlock.start_time.asc())
        .all()
    )

    result = []
    for b in blocks:
        result.append({
            "id": b.id,
            "title": b.title,
            "block_type": b.block_type,
            "status": b.status,
            "start_time": b.start_time.isoformat() if b.start_time else None,
            "end_time": b.end_time.isoformat() if b.end_time else None,
        })
    return result


def detect_schedule_conflicts(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect overlapping time blocks from a list of planner blocks."""
    conflicts = []
    parsed_blocks = []
    for b in blocks:
        if b.get("start_time") and b.get("end_time") and b.get("status") != "cancelled":
            try:
                st = datetime.fromisoformat(b["start_time"])
                et = datetime.fromisoformat(b["end_time"])
                parsed_blocks.append((st, et, b))
            except Exception:
                continue

    parsed_blocks.sort(key=lambda x: x[0])
    for i in range(len(parsed_blocks)):
        for j in range(i + 1, len(parsed_blocks)):
            st1, et1, b1 = parsed_blocks[i]
            st2, et2, b2 = parsed_blocks[j]
            # If next block starts before current block ends, conflict!
            if st2 < et1:
                conflicts.append({
                    "block_1": b1["title"],
                    "block_2": b2["title"],
                    "time_overlap": f"{st2.strftime('%H:%M')} - {min(et1, et2).strftime('%H:%M')}"
                })
    return conflicts


def get_safe_financial_summary(user_id: str, limit_days: int = 30) -> Optional[Dict[str, Any]]:
    """Retrieve high-level, privacy-safe financial overview without exposing individual transaction details."""
    accounts = FinancialAccount.query.filter_by(user_id=user_id, is_active=True, is_archived=False).all()
    if not accounts:
        return None

    total_balance = sum(a.balance for a in accounts)
    currency = accounts[0].currency if accounts else "USD"

    # Aggregated spending/income over the last limit_days
    cutoff = datetime.now(timezone.utc) - timedelta(days=limit_days)
    txs = (
        FinancialTransaction.query
        .join(FinancialAccount, FinancialTransaction.account_id == FinancialAccount.id)
        .filter(
            FinancialAccount.user_id == user_id,
            FinancialTransaction.transaction_date >= cutoff
        )
        .all()
    )

    income = sum(t.amount for t in txs if t.transaction_type == "income")
    expenses = sum(t.amount for t in txs if t.transaction_type == "expense")

    return {
        "active_accounts": len(accounts),
        "total_balance": float(total_balance),
        "currency": currency,
        "recent_income_30d": float(income),
        "recent_expenses_30d": float(expenses),
    }

