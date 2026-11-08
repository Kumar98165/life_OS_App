"""LifeOS - Context Engine.

Synthesizes real-time Tasks, Goals, Habits, and Planner blocks into a
compact, privacy-preserving structured context prompt for the local LLM.
"""
from typing import Dict, Any, Optional
from datetime import date
from app.ai.tools import (
    get_pending_tasks,
    get_today_tasks,
    get_active_goals,
    get_today_habits,
    get_today_schedule
)
from app.models.user import User


class LifeOSContextEngine:
    """Builds authorized LifeOS user context for prompt injection."""

    def build_user_context(self, user_id: str) -> Dict[str, Any]:
        """Query real database tables and assemble structured context dictionary."""
        user = User.query.filter_by(id=user_id).first()
        user_name = user.full_name if user else "User"

        pending_tasks = get_pending_tasks(user_id, limit=6)
        today_tasks = get_today_tasks(user_id, limit=6)
        active_goals = get_active_goals(user_id, limit=4)
        habits = get_today_habits(user_id)
        schedule = get_today_schedule(user_id)

        return {
            "user_name": user_name,
            "today_date": date.today().isoformat(),
            "pending_tasks": pending_tasks,
            "today_tasks": today_tasks,
            "active_goals": active_goals,
            "habits": habits,
            "schedule": schedule,
        }

    def format_context_prompt(self, context: Dict[str, Any]) -> str:
        """Convert structured context dictionary into a concise markdown text block."""
        lines = [
            f"### Current LifeOS Context for {context.get('user_name', 'User')}",
            f"**Today's Date**: {context.get('today_date')}",
            ""
        ]

        # 1. Schedule
        schedule = context.get("schedule", [])
        lines.append("**Today's Schedule (Planner)**:")
        if schedule:
            for b in schedule:
                start = b.get("start_time", "").split("T")[-1][:5] if b.get("start_time") else ""
                end = b.get("end_time", "").split("T")[-1][:5] if b.get("end_time") else ""
                time_range = f"{start} - {end}" if start and end else "Flexible"
                lines.append(f"- [{b.get('status')}] {b.get('title')} ({time_range}, {b.get('block_type')})")
        else:
            lines.append("- No time blocks scheduled for today.")
        lines.append("")

        # 2. Today's Tasks
        today_tasks = context.get("today_tasks", [])
        lines.append("**Today's Tasks**:")
        if today_tasks:
            for t in today_tasks:
                status_icon = "x" if t.get("completed") else " "
                lines.append(f"- [{status_icon}] {t.get('title')} (Priority: {t.get('priority')})")
        else:
            lines.append("- No tasks explicitly due today.")
        lines.append("")

        # 3. Pending Priority Tasks
        pending = context.get("pending_tasks", [])
        lines.append("**Top Pending Priorities**:")
        if pending:
            for t in pending:
                lines.append(f"- {t.get('title')} (Priority: {t.get('priority')}, Status: {t.get('status')})")
        else:
            lines.append("- All pending tasks are up to date.")
        lines.append("")

        # 4. Habits
        habits = context.get("habits", [])
        lines.append("**Habits & Streaks**:")
        if habits:
            for h in habits:
                check = "Done" if h.get("completed_today") else "Pending"
                lines.append(f"- {h.get('title')}: {check} today (Streak: {h.get('current_streak')} days, Frequency: {h.get('frequency')})")
        else:
            lines.append("- No active habits configured.")
        lines.append("")

        # 5. Goals
        goals = context.get("active_goals", [])
        lines.append("**Active Goals**:")
        if goals:
            for g in goals:
                lines.append(f"- {g.get('title')} ({g.get('progress_percent')}% complete, {g.get('completed_milestones')}/{g.get('total_milestones')} milestones)")
        else:
            lines.append("- No active goals in progress.")

        return "\n".join(lines)

