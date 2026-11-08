from datetime import datetime, timezone, date
from decimal import Decimal
from app.extensions import db
from app.models import (
    User, UserPreference, RefreshToken, TaskCategory, Task, Goal, GoalMilestone,
    Habit, HabitLog, PlannerBlock, Note, NoteTag, AIConversation, AIMessage,
    AIMemory, FinancialAccount, FinancialCategory, FinancialTransaction,
    Notification, ActivityLog
)


def test_complete_domain_models_and_cascade(app):
    """Test creating complete user graph across all 14 domains and cascade deletion."""
    with app.app_context():
        # 1. User
        user = User(
            email="fulltest@lifeos.io",
            full_name="Full Model Tester"
        )
        user.set_password("SecurePassword123")
        db.session.add(user)
        db.session.commit()

        # 2. Preferences
        pref = UserPreference(user_id=user.id, theme="light", timezone="America/New_York")
        db.session.add(pref)

        # 3. RefreshToken
        token = RefreshToken(
            user_id=user.id,
            token_jti="test-jti-uuid-12345",
            expires_at=datetime.now(timezone.utc)
        )
        db.session.add(token)

        # 4. Tasks & Category
        cat = TaskCategory(user_id=user.id, name="Deep Work", color_hex="#6C63FF")
        db.session.add(cat)
        db.session.commit()

        task = Task(
            user_id=user.id,
            category_id=cat.id,
            title="Design LifeOS DB Schema",
            priority="high",
            status="in_progress"
        )
        db.session.add(task)

        # 5. Goal & Milestones
        goal = Goal(user_id=user.id, title="Launch LifeOS Product", progress_percent=40.0)
        db.session.add(goal)
        db.session.commit()

        milestone = GoalMilestone(goal_id=goal.id, title="Complete Step 02 DB Architecture", sort_order=1)
        db.session.add(milestone)

        # 6. Habit & HabitLog
        habit = Habit(user_id=user.id, title="Morning Review", frequency="daily")
        db.session.add(habit)
        db.session.commit()

        habit_log = HabitLog(habit_id=habit.id, log_date=date.today(), completed=True)
        db.session.add(habit_log)

        # 7. PlannerBlock
        pblock = PlannerBlock(
            user_id=user.id,
            task_id=task.id,
            title="Focus Block: Database",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            block_type="focus"
        )
        db.session.add(pblock)

        # 8. Note & Tag
        tag = NoteTag(user_id=user.id, name="Architecture")
        db.session.add(tag)
        note = Note(user_id=user.id, title="PostgreSQL Schema Design", content="# DB Design\nNormalized 3NF")
        note.tags.append(tag)
        db.session.add(note)

        # 9. AI Conversation & Message
        conv = AIConversation(user_id=user.id, title="Database Tuning Chat")
        db.session.add(conv)
        db.session.commit()

        msg = AIMessage(conversation_id=conv.id, role="user", content="How do indexes scale in PostgreSQL 18?")
        db.session.add(msg)

        # 10. AI Memory
        mem = AIMemory(
            user_id=user.id,
            memory_key="preferred_theme",
            memory_value="White Glassmorphism",
            memory_type="preference"
        )
        db.session.add(mem)

        # 11 & 12. Finance Accounts, Category & Transaction
        fcat = FinancialCategory(user_id=user.id, name="Software Subscriptions", category_type="expense")
        db.session.add(fcat)
        acc = FinancialAccount(user_id=user.id, name="Primary Checking", balance=Decimal("15000.00"))
        db.session.add(acc)
        db.session.commit()

        trans = FinancialTransaction(
            user_id=user.id,
            account_id=acc.id,
            category_id=fcat.id,
            amount=Decimal("49.99"),
            transaction_type="expense",
            description="Server Hosting",
            transaction_date=datetime.now(timezone.utc)
        )
        db.session.add(trans)

        # 13. Notification
        notif = Notification(user_id=user.id, title="Habit Reminder", body="Time for your Morning Review")
        db.session.add(notif)

        # 14. ActivityLog
        act = ActivityLog(user_id=user.id, action="create", entity_type="task", entity_id=task.id)
        db.session.add(act)

        db.session.commit()

        # Assert all entities persist and are associated with user
        assert user.preferences is not None
        assert user.preferences.timezone == "America/New_York"
        assert len(user.tasks) == 1
        assert len(user.goals) == 1
        assert len(user.habits) == 1
        assert len(user.ai_conversations) == 1
        assert len(user.notes) == 1
        assert len(user.financial_transactions) == 1
        assert len(user.notifications) == 1
        assert len(user.activity_logs) == 1

        # Test CASCADE deletion: deleting user removes all child records cleanly
        db.session.delete(user)
        db.session.commit()

        assert UserPreference.query.filter_by(user_id=user.id).first() is None
        assert Task.query.filter_by(user_id=user.id).first() is None
        assert Goal.query.filter_by(user_id=user.id).first() is None
        assert Habit.query.filter_by(user_id=user.id).first() is None
        assert AIConversation.query.filter_by(user_id=user.id).first() is None
        assert Note.query.filter_by(user_id=user.id).first() is None
        assert FinancialAccount.query.filter_by(user_id=user.id).first() is None
        assert Notification.query.filter_by(user_id=user.id).first() is None
        assert ActivityLog.query.filter_by(user_id=user.id).first() is None

