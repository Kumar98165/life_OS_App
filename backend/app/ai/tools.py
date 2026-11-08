"""LifeOS - Safe Read-Only Agent Tools.

Controlled tools providing authenticated, user-scoped access to Tasks,
Goals, Habits, and Planner blocks without modifying user data.
"""
from datetime import date, datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import selectinload
from app.models.task import Task
from app.models.goal import Goal
from app.models.habit import Habit, HabitLog
from app.models.planner import PlannerBlock


def get_pending_tasks(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve up to limit pending or in-progress tasks for user."""
    tasks = (
        Task.query
        .filter(Task.user_id == user_id, Task.status.in_(["pending", "in_progress"]))
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


def get_today_tasks(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve tasks due on current date for user."""
    today = date.today()
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=timezone.utc)
    end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)

    tasks = (
        Task.query
        .filter(
            Task.user_id == user_id,
            Task.due_date >= start_of_day,
            Task.due_date <= end_of_day
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


def get_today_habits(user_id: str) -> List[Dict[str, Any]]:
    """Retrieve active habits and today's check-in status."""
    today = date.today()
    habits = (
        Habit.query
        .filter(Habit.user_id == user_id, Habit.is_archived.is_(False))
        .order_by(Habit.created_at.desc())
        .all()
    )

    habit_ids = [h.id for h in habits]
    today_logs = {}
    if habit_ids:
        logs = (
            HabitLog.query
            .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.log_date == today)
            .all()
        )
        today_logs = {l.habit_id: l.completed for l in logs}

    is_weekday = today.weekday() < 5
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
            "is_scheduled": is_scheduled,
        })
    return result


def get_today_schedule(user_id: str) -> List[Dict[str, Any]]:
    """Retrieve today's planner blocks in chronological order."""
    today = date.today()
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=timezone.utc)
    end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)
    blocks = (
        PlannerBlock.query
        .filter(
            PlannerBlock.user_id == user_id,
            PlannerBlock.start_time >= start_of_day,
            PlannerBlock.start_time <= end_of_day
        )
        .order_by(PlannerBlock.start_time.asc())
        .all()
    )
    return [
        {
            "id": b.id,
            "title": b.title,
            "block_type": b.block_type,
            "status": b.status,
            "start_time": b.start_time.isoformat() if b.start_time else None,
            "end_time": b.end_time.isoformat() if b.end_time else None,
        }
        for b in blocks
    ]
