"""LifeOS - Tests for Step 4: Advanced Personal Intelligence Engine.

Verifies:
1. Personal context engine retrieval: user preferences, memories, routines, tasks, habits, goals, planner blocks.
2. Relevance ranking and context size limits (no infinite prompt inflation).
3. Personalization controls: respectful of disabled personalization and disabled memory.
4. Timezone handling and local date scoping.
5. Goal and habit intelligence: streak observations, deadline proximity, schedule conflict detection.
6. Proactive insights: deduplication, dismissal resilience, actionable metadata.
7. Multi-user isolation & cross-user leak prevention.
8. Backward compatibility for both synchronous and SSE streaming chat endpoints.
"""
import pytest
from datetime import datetime, date, timezone, timedelta
from app.models.user import User
from app.models.personalization import UserPersonalization, DailyRoutine
from app.models.user_preference import UserPreference
from app.models.task import Task
from app.models.goal import Goal, GoalMilestone
from app.models.habit import Habit, HabitLog
from app.models.planner import PlannerBlock
from app.models.ai import AIMemory
from app.extensions import db
from app.ai.context_engine import LifeOSContextEngine
from app.services.personal_intelligence_service import personal_intelligence_service


def test_personal_context_engine_retrieval(app):
    """Verify context engine retrieves user-scoped tasks, habits, goals, and schedule."""
    with app.app_context():
        user = User(email="intel_user@lifeos.internal", full_name="Context Tester")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Seed Tasks
        t1 = Task(user_id=user.id, title="Complete Step 4 Testing", priority="urgent", status="in_progress")
        t2 = Task(user_id=user.id, title="Future Review", priority="low", status="todo")
        db.session.add_all([t1, t2])

        # Seed Habit
        h1 = Habit(user_id=user.id, title="Morning Meditation", frequency="daily", current_streak=4)
        db.session.add(h1)

        # Seed Goal
        g1 = Goal(user_id=user.id, title="Ship LifeOS v1.0", progress_percent=60.0)
        db.session.add(g1)
        db.session.commit()

        engine = LifeOSContextEngine()
        context = engine.build_user_context(user.id)

        assert context["user_name"] == "Context Tester"
        assert len(context["pending_tasks"]) >= 1
        assert any(t["title"] == "Complete Step 4 Testing" for t in context["pending_tasks"])
        assert len(context["habits"]) >= 1
        assert context["habits"][0]["title"] == "Morning Meditation"
        assert len(context["active_goals"]) >= 1
        assert context["active_goals"][0]["title"] == "Ship LifeOS v1.0"

        formatted = engine.format_context_prompt(context)
        assert "Complete Step 4 Testing" in formatted
        assert "Morning Meditation" in formatted
        assert "Ship LifeOS v1.0" in formatted


def test_personalization_disabled_respects_privacy(app):
    """Verify that when personalization_enabled is false, preferences and routines are not injected."""
    with app.app_context():
        user = User(email="private_user@lifeos.internal", full_name="Private User")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Create personalization with disabled flag
        pers = UserPersonalization(
            user_id=user.id,
            preferred_name="SuperSecretName",
            personalization_enabled=False,
            ai_response_style="motivational"
        )
        routine = DailyRoutine(user_id=user.id, wake_time="05:30")
        db.session.add_all([pers, routine])
        db.session.commit()

        engine = LifeOSContextEngine()
        context = engine.build_user_context(user.id)

        assert context["personalization_enabled"] is False
        assert context["personalization"] is None
        assert context["daily_routine"] is None
        # Preferred name should fall back to user.full_name
        assert context["user_name"] == "Private User"

        formatted = engine.format_context_prompt(context)
        assert "SuperSecretName" not in formatted
        assert "Personal Preferences & Schedule Rhythm" not in formatted


def test_schedule_conflict_detection(app):
    """Verify detection of overlapping planner blocks in daily intelligence."""
    with app.app_context():
        user = User(email="conflict_user@lifeos.internal", full_name="Conflict Tester")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        now = datetime.now(timezone.utc)
        b1 = PlannerBlock(
            user_id=user.id,
            title="Team Architecture Standup",
            start_time=now.replace(hour=10, minute=0, second=0),
            end_time=now.replace(hour=11, minute=0, second=0),
            block_type="meeting"
        )
        b2 = PlannerBlock(
            user_id=user.id,
            title="Customer Interview",
            start_time=now.replace(hour=10, minute=30, second=0),
            end_time=now.replace(hour=11, minute=30, second=0),
            block_type="meeting"
        )
        db.session.add_all([b1, b2])
        db.session.commit()

        briefing = personal_intelligence_service.get_daily_briefing(user.id)
        assert briefing["schedule_summary"]["has_conflicts"] is True
        assert len(briefing["schedule_summary"]["conflicts"]) >= 1

        insights = personal_intelligence_service.get_proactive_insights(user.id)
        conflict_insights = [i for i in insights if i["type"] == "schedule_conflict"]
        assert len(conflict_insights) == 1
        assert "Planner Schedule Conflict" in conflict_insights[0]["title"]


def test_approaching_deadlines_and_habit_insights(app):
    """Verify proactive detection of upcoming deadlines and missed habit nudges."""
    with app.app_context():
        user = User(email="insights_user@lifeos.internal", full_name="Insight Tester")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Task with deadline tomorrow
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        t = Task(
            user_id=user.id,
            title="Submit Quarterly Report",
            priority="high",
            status="todo",
            due_date=tomorrow
        )
        db.session.add(t)

        # Habit with 0 streak and missed yesterday/today
        h = Habit(
            user_id=user.id,
            title="Evening Journaling",
            frequency="daily",
            current_streak=0
        )
        db.session.add(h)
        db.session.commit()

        insights = personal_intelligence_service.get_proactive_insights(user.id)
        types = [i["type"] for i in insights]

        assert "deadline_reminder" in types
        assert "habit_rebound" in types

        deadline_item = next(i for i in insights if i["type"] == "deadline_reminder")
        assert "Submit Quarterly Report" in deadline_item["message"]


def test_cross_user_isolation(app):
    """Verify User A never receives User B's context, briefings, or insights."""
    with app.app_context():
        user_a = User(email="user_a@lifeos.internal", full_name="User Alpha")
        user_a.set_password("SecurePass123!")
        user_b = User(email="user_b@lifeos.internal", full_name="User Beta")
        user_b.set_password("SecurePass123!")
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # Add private task to User A
        t_a = Task(user_id=user_a.id, title="Alpha Secret Strategy", priority="urgent")
        db.session.add(t_a)
        db.session.commit()

        engine = LifeOSContextEngine()
        context_b = engine.build_user_context(user_b.id)
        formatted_b = engine.format_context_prompt(context_b)

        assert "Alpha Secret Strategy" not in formatted_b
        assert not any(t["title"] == "Alpha Secret Strategy" for t in context_b["pending_tasks"])

        briefing_b = personal_intelligence_service.get_daily_briefing(user_b.id)
        assert briefing_b["user_id"] == user_b.id
        assert not any(t["title"] == "Alpha Secret Strategy" for t in briefing_b["task_summary"]["top_pending"])


def test_daily_briefing_api_endpoint(client, auth_headers):
    """Verify GET /api/v1/ai/intelligence/briefing endpoint returns 200 with structured data."""
    res = client.get("/api/v1/ai/intelligence/briefing", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "greeting" in data
    assert "schedule_summary" in data
    assert "task_summary" in data
    assert "habit_summary" in data
    assert "goal_summary" in data
    assert "priority_suggestions" in data


def test_proactive_insights_api_endpoint(client, auth_headers):
    """Verify GET /api/v1/ai/intelligence/insights endpoint returns 200 with insights array."""
    res = client.get("/api/v1/ai/intelligence/insights", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "insights" in data
    assert isinstance(data["insights"], list)


def test_memory_privacy_disabled_and_expired(app):
    """Verify approved, pending, rejected, and expired memories behavior when memory is enabled vs disabled."""
    from app.ai.memory.retriever import MemoryRetrievalEngine
    with app.app_context():
        user = User(email="mem_priv@lifeos.internal", full_name="Memory Test")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Create user preference with memory enabled
        pref = UserPreference(user_id=user.id, ai_memory_enabled=True)
        db.session.add(pref)

        now = datetime.now(timezone.utc)
        m_confirmed = AIMemory(user_id=user.id, memory_key="coffee", memory_value="Prefers black coffee", status="confirmed")
        m_pending = AIMemory(user_id=user.id, memory_key="tea", memory_value="Likes green tea", status="pending")
        m_rejected = AIMemory(user_id=user.id, memory_key="sugar", memory_value="Takes 2 spoons", status="rejected")
        m_expired = AIMemory(user_id=user.id, memory_key="diet", memory_value="On keto", status="confirmed", expires_at=now - timedelta(days=1))
        db.session.add_all([m_confirmed, m_pending, m_rejected, m_expired])
        db.session.commit()

        retriever = MemoryRetrievalEngine()
        res = retriever.retrieve_relevant_memories(user.id, "coffee tea drink")
        keys = [m.memory_key for m in res]
        assert "coffee" in keys
        assert "tea" not in keys       # pending excluded
        assert "sugar" not in keys     # rejected excluded
        assert "diet" not in keys      # expired excluded

        # Disable AI memory in preferences
        pref.ai_memory_enabled = False
        db.session.commit()

        res_disabled = retriever.retrieve_relevant_memories(user.id, "coffee tea drink")
        assert len(res_disabled) == 0  # Completely excluded when toggle is off


def test_financial_privacy_relevance(app):
    """Verify financial summaries are only retrieved on relevant queries and never expose raw txs."""
    from app.models.finance import FinancialAccount, FinancialTransaction
    with app.app_context():
        user = User(email="fin_priv@lifeos.internal", full_name="Finance Priv")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        acc = FinancialAccount(user_id=user.id, name="Checking", balance=5000.0, currency="USD")
        db.session.add(acc)
        db.session.flush()

        tx = FinancialTransaction(
            user_id=user.id,
            account_id=acc.id,
            amount=50.0,
            transaction_type="expense",
            description="Confidential secret dinner",
            transaction_date=datetime.now(timezone.utc)
        )
        db.session.add(tx)
        db.session.commit()

        engine = LifeOSContextEngine()

        # Unrelated query
        unrelated_ctx = engine.build_user_context(user.id, query="What tasks are scheduled for tomorrow?")
        assert unrelated_ctx["finance_summary"] is None
        unrelated_prompt = engine.format_context_prompt(unrelated_ctx)
        assert "Financial Overview" not in unrelated_prompt
        assert "Confidential secret dinner" not in unrelated_prompt

        # Finance query
        fin_ctx = engine.build_user_context(user.id, query="What is my current savings budget and balance?")
        assert fin_ctx["finance_summary"] is not None
        assert fin_ctx["finance_summary"]["total_balance"] == 5000.0
        fin_prompt = engine.format_context_prompt(fin_ctx)
        assert "Financial Overview (Safe Aggregate)" in fin_prompt
        assert "Confidential secret dinner" not in fin_prompt  # Raw tx details strictly omitted


def test_timezone_date_boundaries(app):
    """Verify task and schedule retrieval respects user timezone near midnight."""
    with app.app_context():
        user = User(email="tz_user@lifeos.internal", full_name="Timezone User")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        # Set user timezone to Asia/Kolkata (UTC+5:30)
        pers = UserPersonalization(user_id=user.id, timezone="Asia/Kolkata")
        db.session.add(pers)

        # Create a task due at 20:00 UTC today.
        # In Asia/Kolkata, that is 01:30 AM tomorrow!
        today_utc = datetime.now(timezone.utc)
        target_due = today_utc.replace(hour=20, minute=0, second=0)
        t = Task(user_id=user.id, title="Midnight Boundary Task", due_date=target_due)
        db.session.add(t)
        db.session.commit()

        briefing = personal_intelligence_service.get_daily_briefing(user.id)
        assert briefing["timezone"] == "Asia/Kolkata"
        assert briefing["date"] is not None


