"""LifeOS - Personal Context Engine.

Synthesizes real-time Tasks, Goals, Habits, Planner blocks, Financial overviews,
and Personal Preferences into a compact, privacy-preserving, ranked context prompt
for the local LLM. Enforces token budgets, relevance ranking, and multi-user isolation.
"""
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from app.ai.tools import (
    get_pending_tasks,
    get_today_tasks,
    get_approaching_deadlines,
    get_active_goals,
    get_today_habits,
    get_today_schedule,
    detect_schedule_conflicts,
    get_safe_financial_summary
)
from app.models.user import User
from app.models.personalization import UserPersonalization, DailyRoutine
from app.models.user_preference import UserPreference


class LifeOSContextEngine:
    """Builds authorized, relevance-ranked LifeOS user context for prompt injection."""

    def build_user_context(
        self,
        user_id: str,
        query: Optional[str] = None,
        include_sensitive_finance: bool = False
    ) -> Dict[str, Any]:
        """Query real database tables and assemble structured, relevance-filtered context dictionary."""
        user = User.query.filter_by(id=user_id).first()
        personalization = UserPersonalization.query.filter_by(user_id=user_id).first()
        routine = DailyRoutine.query.filter_by(user_id=user_id).first()
        user_pref = UserPreference.query.filter_by(user_id=user_id).first()

        # Check if personalization is globally enabled for this user
        is_personalization_active = True
        if personalization and not personalization.personalization_enabled:
            is_personalization_active = False

        # Determine user timezone and local date
        tz_name = "UTC"
        if is_personalization_active and personalization and personalization.timezone:
            tz_name = personalization.timezone
        elif user_pref and user_pref.timezone:
            tz_name = user_pref.timezone

        try:
            user_tz = ZoneInfo(tz_name)
            today_local = datetime.now(user_tz).date()
        except Exception:
            user_tz = timezone.utc
            today_local = date.today()

        user_name = (
            personalization.preferred_name
            if (is_personalization_active and personalization and personalization.preferred_name)
            else (user.full_name if user else "User")
        )

        query_lower = (query or "").lower()

        # 1. Tasks: Today tasks + pending priority tasks + approaching deadlines
        pending_tasks = get_pending_tasks(user_id, limit=6)
        today_tasks = get_today_tasks(user_id, limit=6, target_date=today_local, tz_name=tz_name)
        approaching_deadlines = get_approaching_deadlines(user_id, days_ahead=3, limit=4, tz_name=tz_name)

        # 2. Goals & Milestones
        active_goals = get_active_goals(user_id, limit=4)

        # 3. Habits & Streaks
        habits = get_today_habits(user_id, target_date=today_local, tz_name=tz_name)

        # 4. Schedule & Conflicts
        schedule = get_today_schedule(user_id, target_date=today_local, tz_name=tz_name)
        conflicts = detect_schedule_conflicts(schedule)

        # 5. Finance: Only retrieved when relevant to query and explicitly permitted
        finance_summary = None
        finance_keywords = ["money", "finance", "spend", "expense", "budget", "saving", "balance", "cost", "account"]
        if include_sensitive_finance or any(k in query_lower for k in finance_keywords):
            finance_summary = get_safe_financial_summary(user_id, limit_days=30)

        # 6. Intent & Context Focus Filtering (budgeting token limits)
        return {
            "user_name": user_name,
            "today_date": today_local.isoformat(),
            "timezone": tz_name,
            "pending_tasks": pending_tasks,
            "today_tasks": today_tasks,
            "approaching_deadlines": approaching_deadlines,
            "active_goals": active_goals,
            "habits": habits,
            "schedule": schedule,
            "conflicts": conflicts,
            "finance_summary": finance_summary,
            "personalization": personalization.to_dict() if (is_personalization_active and personalization) else None,
            "daily_routine": routine.to_dict() if (is_personalization_active and routine) else None,
            "personalization_enabled": is_personalization_active,
        }

    def format_context_prompt(self, context: Dict[str, Any], max_items_per_section: int = 5) -> str:
        """Convert structured context dictionary into a concise markdown text block adhering to model context budget."""
        lines = [
            f"### Current LifeOS Context for {context.get('user_name', 'User')}",
            f"**Today's Date**: {context.get('today_date')} (Timezone: {context.get('timezone', 'UTC')})",
            ""
        ]

        # User Personalization & Routine context
        p = context.get("personalization")
        r = context.get("daily_routine")
        if p or r:
            lines.append("**Personal Preferences & Schedule Rhythm**:")
            if p:
                lines.append(
                    f"- Productivity Style: {p.get('productivity_style')}, Priority Strategy: {p.get('task_priority_strategy')}"
                )
                lines.append(
                    f"- AI Desired Style: {p.get('ai_response_style')}, Length: {p.get('ai_response_length')}, Language: {p.get('preferred_language')}"
                )
            if r:
                lines.append(
                    f"- Working Hours: {r.get('work_start')} - {r.get('work_end')}, Planning Time: {r.get('preferred_planning_time')}"
                )
                lines.append(
                    f"- Sleep/Wake Rhythm: Wake at {r.get('wake_time')}, Sleep at {r.get('sleep_time')}"
                )
            lines.append("")

        # 1. Schedule & Conflicts
        schedule = context.get("schedule", [])
        conflicts = context.get("conflicts", [])
        lines.append("**Today's Schedule (Planner)**:")
        if schedule:
            for b in schedule[:max_items_per_section]:
                start = b.get("start_time", "").split("T")[-1][:5] if b.get("start_time") else ""
                end = b.get("end_time", "").split("T")[-1][:5] if b.get("end_time") else ""
                time_range = f"{start} - {end}" if start and end else "Flexible"
                lines.append(f"- [{b.get('status')}] {b.get('title')} ({time_range}, {b.get('block_type')})")
        else:
            lines.append("- No time blocks scheduled for today.")

        if conflicts:
            lines.append("  *SCHEDULE CONFLICT WARNING*:")
            for c in conflicts:
                lines.append(f"  - Conflict detected between '{c['block_1']}' and '{c['block_2']}' around {c['time_overlap']}")
        lines.append("")

        # 2. Today's Tasks & Approaching Deadlines
        today_tasks = context.get("today_tasks", [])
        lines.append("**Today's Tasks**:")
        if today_tasks:
            for t in today_tasks[:max_items_per_section]:
                status_icon = "x" if t.get("completed") else " "
                lines.append(f"- [{status_icon}] {t.get('title')} (Priority: {t.get('priority')})")
        else:
            lines.append("- No tasks explicitly due today.")

        deadlines = context.get("approaching_deadlines", [])
        if deadlines:
            lines.append("**Approaching Deadlines (Next 3 Days)**:")
            for d in deadlines[:max_items_per_section]:
                due_str = d.get('due_date', '').split('T')[0] if d.get('due_date') else 'Soon'
                lines.append(f"- {d.get('title')} (Due: {due_str}, Priority: {d.get('priority')})")
        lines.append("")

        # 3. Pending Priority Tasks
        pending = context.get("pending_tasks", [])
        lines.append("**Top Pending Priorities**:")
        if pending:
            for t in pending[:max_items_per_section]:
                lines.append(f"- {t.get('title')} (Priority: {t.get('priority')}, Status: {t.get('status')})")
        else:
            lines.append("- All pending tasks are up to date.")
        lines.append("")

        # 4. Habits & Consistency
        habits = context.get("habits", [])
        lines.append("**Habits & Streaks**:")
        if habits:
            for h in habits[:max_items_per_section]:
                check = "Done" if h.get("completed_today") else "Pending"
                streak_text = f"Streak: {h.get('current_streak')} days"
                if not h.get("completed_today") and not h.get("completed_yesterday") and h.get("current_streak", 0) == 0:
                    streak_text += " (Missed last 2 days)"
                lines.append(f"- {h.get('title')}: {check} today ({streak_text}, Frequency: {h.get('frequency')})")
        else:
            lines.append("- No active habits configured.")
        lines.append("")

        # 5. Goals
        goals = context.get("active_goals", [])
        lines.append("**Active Goals**:")
        if goals:
            for g in goals[:max_items_per_section]:
                target_str = f", Target: {g.get('target_date').split('T')[0]}" if g.get('target_date') else ""
                lines.append(f"- {g.get('title')} ({g.get('progress_percent')}% complete, {g.get('completed_milestones')}/{g.get('total_milestones')} milestones{target_str})")
        else:
            lines.append("- No active goals in progress.")

        # 6. Safe Finance Summary (Only when present)
        fin = context.get("finance_summary")
        if fin:
            lines.append("")
            lines.append("**Financial Overview (Safe Aggregate)**:")
            lines.append(f"- Total Balance: {fin.get('currency')} {fin.get('total_balance'):,.2f} across {fin.get('active_accounts')} accounts")
            lines.append(f"- Last 30 Days Cash Flow: +{fin.get('currency')} {fin.get('recent_income_30d'):,.2f} in / -{fin.get('currency')} {fin.get('recent_expenses_30d'):,.2f} out")

        return "\n".join(lines)


