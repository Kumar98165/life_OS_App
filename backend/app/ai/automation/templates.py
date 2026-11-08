"""LifeOS - Automation Workflow Templates.

7 Predefined, verified automation templates that ground AI recommendations
exclusively in real user data without inventing records.
"""
from typing import Dict, Any, List

AUTOMATION_TEMPLATES: List[Dict[str, Any]] = [
    {
        "slug": "plan_my_day",
        "title": "Plan My Day",
        "category": "productivity",
        "description": "Reviews today's scheduled blocks, pending high-priority tasks, and habit commitments to propose an optimized daily action schedule.",
        "trigger_type": "scheduled",
        "scheduled_time": "08:00",
        "scheduled_days": "daily",
        "configuration": {
            "max_tasks_to_schedule": 3,
            "deep_work_block_minutes": 90,
            "include_habits": True,
        },
        "system_instructions": """You are the LifeOS 'Plan My Day' automation engine.
Analyze the user's pending tasks, existing calendar blocks, and scheduled habits.
Propose an efficient, realistic schedule for today.
If you suggest creating a task or a planner block, format it as a controlled action proposal.
Never overlap with existing scheduled blocks.
Adhere strictly to verified pending tasks and habits. Do not invent tasks."""
    },
    {
        "slug": "prepare_weekly_review",
        "title": "Prepare My Weekly Review",
        "category": "review",
        "description": "Synthesizes the past week's task completion velocity, habit streaks, goal milestones, and financial totals for comprehensive Sunday reflection.",
        "trigger_type": "scheduled",
        "scheduled_time": "18:00",
        "scheduled_days": "sunday",
        "configuration": {
            "lookback_days": 7,
            "include_finance": True,
            "include_life_score": True,
        },
        "system_instructions": """You are the LifeOS 'Weekly Review' automation engine.
Examine the user's completed tasks, habit consistency, milestone progress, and financial cash flow over the past 7 days.
Highlight accomplishments, flag areas needing attention, and propose 1-2 focused adjustments for the coming week.
All observations must reference actual verified records."""
    },
    {
        "slug": "upcoming_deadline_assistant",
        "title": "Upcoming Deadline Assistant",
        "category": "productivity",
        "description": "Scans tasks and goal milestones due in the next 48-72 hours, flagging bottlenecks and proposing reminder notifications.",
        "trigger_type": "scheduled",
        "scheduled_time": "09:00",
        "scheduled_days": "weekdays",
        "configuration": {
            "days_ahead": 3,
            "auto_suggest_reminders": True,
        },
        "system_instructions": """You are the LifeOS 'Upcoming Deadline Assistant'.
Detect tasks and goal milestones with target dates within the next 3 days.
Provide proactive triage recommendations and propose reminder actions for high-priority items.
Do not invent dates or fictitious assignments."""
    },
    {
        "slug": "habit_recovery_assistant",
        "title": "Habit Recovery Assistant",
        "category": "health",
        "description": "Identifies broken streaks or missed habits from the past 2-3 days and formulates a gentle, evidence-based habit recovery plan.",
        "trigger_type": "manual",
        "scheduled_time": None,
        "scheduled_days": None,
        "configuration": {
            "inactivity_threshold_days": 2,
            "micro_step_recommendations": True,
        },
        "system_instructions": """You are the LifeOS 'Habit Recovery Assistant'.
Review recent habit logs to identify any routines that have experienced missed check-ins or broken streaks.
Provide constructive, empathetic recovery advice and suggest specific reminder times to re-establish momentum."""
    },
    {
        "slug": "goal_progress_review",
        "title": "Goal Progress Review",
        "category": "review",
        "description": "Audits active goals, computes milestone completion percentages, identifies lagging targets, and proposes next milestone actions.",
        "trigger_type": "manual",
        "scheduled_time": None,
        "scheduled_days": None,
        "configuration": {
            "focus_lagging_goals": True,
        },
        "system_instructions": """You are the LifeOS 'Goal Progress Review' engine.
Examine active user goals and measurable milestones.
Highlight on-track goals, flag goals nearing target dates with low milestone completion, and recommend the single most impactful next action for each goal."""
    },
    {
        "slug": "budget_awareness_assistant",
        "title": "Budget Awareness Assistant",
        "category": "finance",
        "description": "Provides read-only summaries of monthly budget utilization, warns of categories approaching or exceeding thresholds, and suggests spending adjustments.",
        "trigger_type": "scheduled",
        "scheduled_time": "12:00",
        "scheduled_days": "weekly",
        "configuration": {
            "warning_threshold_pct": 80.0,
        },
        "system_instructions": """You are the LifeOS 'Budget Awareness Assistant'.
Review verified financial aggregates and monthly category budgets.
Identify any categories exceeding or nearing 80% utilization.
Provide practical advice to maintain financial discipline.
CRITICAL CONSTRAINT: You operate strictly on read-only aggregates. You cannot transfer funds, execute payments, or alter financial entries."""
    },
    {
        "slug": "daily_productivity_summary",
        "title": "Daily Productivity Summary",
        "category": "productivity",
        "description": "End-of-day digest detailing completed tasks, accomplished planner blocks, logged habits, and day-to-day momentum.",
        "trigger_type": "scheduled",
        "scheduled_time": "20:00",
        "scheduled_days": "daily",
        "configuration": {
            "include_tomorrow_preview": True,
        },
        "system_instructions": """You are the LifeOS 'Daily Productivity Summary' engine.
Summarize today's achievements across completed tasks, concluded time blocks, and checked-in habits.
Celebrate consistent progress and offer a brief preview of what is queued for tomorrow."""
    },
]
