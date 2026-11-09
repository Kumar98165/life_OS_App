"""LifeOS - Personal Intelligence Service.

Coordinates deterministic rule-based daily analysis, goal and habit observations,
proactive insight generation, and schedule conflict detection for LifeOS users.
Designed for CPU efficiency, zero cloud dependency, and multi-user isolation.
"""
import logging
from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any, List, Optional
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

logger = logging.getLogger(__name__)


class PersonalIntelligenceService:
    """Core intelligence engine delivering personalized daily briefings, goal & habit observations, and proactive insights."""

    def get_daily_briefing(self, user_id: str) -> Dict[str, Any]:
        """Synthesize a complete daily intelligence summary: planner, pending tasks, deadlines, habits, and goals."""
        personalization = UserPersonalization.query.filter_by(user_id=user_id).first()
        routine = DailyRoutine.query.filter_by(user_id=user_id).first()
        user_pref = UserPreference.query.filter_by(user_id=user_id).first()
        user = User.query.filter_by(id=user_id).first()

        is_pers_active = personalization.personalization_enabled if personalization else True
        tz_name = (personalization.timezone if (is_pers_active and personalization and personalization.timezone)
                   else (user_pref.timezone if (user_pref and user_pref.timezone) else "UTC"))

        try:
            user_tz = ZoneInfo(tz_name)
            today_local = datetime.now(user_tz).date()
        except Exception:
            user_tz = timezone.utc
            today_local = date.today()

        user_name = (personalization.preferred_name if (is_pers_active and personalization and personalization.preferred_name)
                     else (user.full_name if user else "Friend"))

        # Facts from database
        today_tasks = get_today_tasks(user_id, limit=10, target_date=today_local, tz_name=tz_name)
        pending_tasks = get_pending_tasks(user_id, limit=8)
        approaching_deadlines = get_approaching_deadlines(user_id, days_ahead=3, limit=5, tz_name=tz_name)
        active_goals = get_active_goals(user_id, limit=5)
        habits = get_today_habits(user_id, target_date=today_local, tz_name=tz_name)
        schedule = get_today_schedule(user_id, target_date=today_local, tz_name=tz_name)
        conflicts = detect_schedule_conflicts(schedule)

        # Build dynamic priority suggestions based on user productivity strategy
        priority_strategy = personalization.task_priority_strategy if (is_pers_active and personalization) else "eisenhower"
        suggestions = self._generate_priority_suggestions(
            today_tasks=today_tasks,
            pending_tasks=pending_tasks,
            deadlines=approaching_deadlines,
            conflicts=conflicts,
            strategy=priority_strategy
        )

        completed_tasks_count = sum(1 for t in today_tasks if t.get("completed"))
        total_today_tasks = len(today_tasks)

        completed_habits_count = sum(1 for h in habits if h.get("completed_today"))
        total_habits = len(habits)

        # Dynamic greeting based on time of day
        now_hour = datetime.now(user_tz).hour
        if 5 <= now_hour < 12:
            time_greeting = "Good morning"
        elif 12 <= now_hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        greeting = f"{time_greeting}, {user_name}!"

        return {
            "user_id": user_id,
            "date": today_local.isoformat(),
            "timezone": tz_name,
            "greeting": greeting,
            "schedule_summary": {
                "total_blocks": len(schedule),
                "has_conflicts": len(conflicts) > 0,
                "conflicts": conflicts,
                "blocks": schedule,
            },
            "task_summary": {
                "total_today": total_today_tasks,
                "completed_today": completed_tasks_count,
                "pending_priority_count": len(pending_tasks),
                "approaching_deadlines_count": len(approaching_deadlines),
                "today_tasks": today_tasks,
                "top_pending": pending_tasks[:5],
                "approaching_deadlines": approaching_deadlines,
            },
            "habit_summary": {
                "total_habits": total_habits,
                "completed_today": completed_habits_count,
                "habits": habits,
            },
            "goal_summary": {
                "active_goals_count": len(active_goals),
                "goals": active_goals,
            },
            "priority_suggestions": suggestions,
        }

    def get_proactive_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate deduplicated, actionable, deterministic observations across tasks, schedule, habits, and goals."""
        briefing = self.get_daily_briefing(user_id)
        insights: List[Dict[str, Any]] = []

        # 1. Schedule Conflict Insight
        conflicts = briefing["schedule_summary"]["conflicts"]
        if conflicts:
            insights.append({
                "id": f"insight-conflict-{briefing['date']}",
                "type": "schedule_conflict",
                "category": "schedule",
                "severity": "warning",
                "title": "Planner Schedule Conflict Detected",
                "message": f"You have an overlap between '{conflicts[0]['block_1']}' and '{conflicts[0]['block_2']}' around {conflicts[0]['time_overlap']}. Consider adjusting the block timing.",
                "actionable": True,
                "target_screen": "PlannerTab"
            })

        # 2. Approaching Deadline Observation
        deadlines = briefing["task_summary"]["approaching_deadlines"]
        if deadlines:
            urgent_task = deadlines[0]
            insights.append({
                "id": f"insight-deadline-{urgent_task['id']}",
                "type": "deadline_reminder",
                "category": "tasks",
                "severity": "info",
                "title": "Upcoming Priority Deadline",
                "message": f"'{urgent_task['title']}' is due on {urgent_task['due_date'].split('T')[0]}. Planning dedicated focus time early will prevent last-minute rush.",
                "actionable": True,
                "target_screen": "TasksTab"
            })

        # 3. Habit Consistency / Missed Streak Observation
        habits = briefing["habit_summary"]["habits"]
        for h in habits:
            # If habit was missed yesterday and not yet completed today
            if not h.get("completed_today") and not h.get("completed_yesterday") and h.get("current_streak", 0) == 0:
                insights.append({
                    "id": f"insight-habit-rebound-{h['id']}",
                    "type": "habit_rebound",
                    "category": "habits",
                    "severity": "nudge",
                    "title": f"Resume Your '{h['title']}' Habit",
                    "message": f"A short 5-minute session today will help you rebuild momentum for your {h['title']} habit.",
                    "actionable": True,
                    "target_screen": "Habits"
                })
                break  # Show at most one habit nudge to avoid overwhelming
            elif h.get("current_streak", 0) >= 5 and not h.get("completed_today"):
                insights.append({
                    "id": f"insight-habit-streak-{h['id']}",
                    "type": "habit_streak",
                    "category": "habits",
                    "severity": "celebration",
                    "title": f"{h['current_streak']}-Day Streak on '{h['title']}'",
                    "message": f"Great consistency! Complete '{h['title']}' today to reach a {h['current_streak'] + 1}-day streak.",
                    "actionable": True,
                    "target_screen": "Habits"
                })
                break

        # 4. Goal Progress Observation
        goals = briefing["goal_summary"]["goals"]
        for g in goals:
            if g.get("progress_percent", 0) >= 75 and g.get("progress_percent", 0) < 100:
                insights.append({
                    "id": f"insight-goal-finish-{g['id']}",
                    "type": "goal_momentum",
                    "category": "goals",
                    "severity": "info",
                    "title": f"Goal Close to Completion: {g['title']}",
                    "message": f"You're at {g['progress_percent']}% progress with {g['completed_milestones']}/{g['total_milestones']} milestones finished. The finish line is in sight!",
                    "actionable": True,
                    "target_screen": "GoalsTab"
                })
                break

        # 5. Daily Planning Suggestion if planner is completely empty but tasks exist
        if briefing["schedule_summary"]["total_blocks"] == 0 and briefing["task_summary"]["total_today"] > 0:
            insights.append({
                "id": f"insight-plan-day-{briefing['date']}",
                "type": "daily_planning",
                "category": "planner",
                "severity": "suggestion",
                "title": "Time-Block Your Day",
                "message": f"You have {briefing['task_summary']['total_today']} task(s) scheduled for today. Allocating time blocks in your Planner will help protect focused work time.",
                "actionable": True,
                "target_screen": "PlannerTab"
            })

        return insights

    def _generate_priority_suggestions(
        self,
        today_tasks: List[Dict[str, Any]],
        pending_tasks: List[Dict[str, Any]],
        deadlines: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        strategy: str = "eisenhower"
    ) -> List[str]:
        """Generate clear, non-hallucinatory daily priority recommendations based on facts."""
        suggestions = []

        if conflicts:
            suggestions.append(f"Resolve the schedule conflict between '{conflicts[0]['block_1']}' and '{conflicts[0]['block_2']}' to ensure uninterrupted focus.")

        uncompleted_today = [t for t in today_tasks if not t.get("completed")]
        if uncompleted_today:
            # Sort according to user priority strategy
            if strategy == "deadline_first" and deadlines:
                suggestions.append(f"Tackle '{deadlines[0]['title']}' first as it approaches its deadline.")
            elif strategy == "impact_first":
                high_p = [t for t in uncompleted_today if t.get("priority") in ["urgent", "high"]]
                if high_p:
                    suggestions.append(f"Focus on your highest-impact task: '{high_p[0]['title']}'.")
                else:
                    suggestions.append(f"Start with '{uncompleted_today[0]['title']}'.")
            else:
                # Default / Eisenhower
                high_p = [t for t in uncompleted_today if t.get("priority") in ["urgent", "high"]]
                if high_p:
                    suggestions.append(f"Prioritize '{high_p[0]['title']}' today as your critical priority.")
                else:
                    suggestions.append(f"Work through today's planned task: '{uncompleted_today[0]['title']}'.")

        elif pending_tasks:
            suggestions.append(f"No tasks explicitly due today. Consider advancing pending priority '{pending_tasks[0]['title']}'.")
        else:
            suggestions.append("Your priority queue is clear today. Great opportunity for deep learning or review.")

        return suggestions


personal_intelligence_service = PersonalIntelligenceService()

