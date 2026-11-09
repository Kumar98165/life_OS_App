from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from app.extensions import db
from app.models.focus import FocusGoal, FocusSession, FocusDistraction
from app.models.task import Task
from app.models.planner import PlannerBlock
from app.core.exceptions import NotFoundException, BadRequestException


class FocusService:
    """Deterministic business logic for focus sessions, pomodoro timers, and statistics."""

    def get_or_create_goal(self, user_id: str) -> FocusGoal:
        goal = FocusGoal.query.filter_by(user_id=user_id).first()
        if not goal:
            goal = FocusGoal(
                user_id=user_id,
                daily_target_minutes=120,
                weekly_target_minutes=600,
                preferred_technique="25/5",
                custom_work_minutes=25,
                custom_break_minutes=5,
                custom_long_break_minutes=15,
                long_break_interval=4
            )
            db.session.add(goal)
            db.session.commit()
        return goal

    def update_goal(self, user_id: str, data: Dict[str, Any]) -> FocusGoal:
        goal = self.get_or_create_goal(user_id)
        for k, v in data.items():
            if v is not None and hasattr(goal, k):
                setattr(goal, k, v)
        db.session.commit()
        return goal

    def start_session(
        self,
        user_id: str,
        title: str = "Focus Session",
        session_type: str = "work",
        target_duration_minutes: int = 25,
        task_id: Optional[str] = None,
        planner_block_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> FocusSession:
        # Validate task if provided
        if task_id:
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if not task:
                raise NotFoundException("Task not found or unauthorized")

        # Validate planner block if provided
        if planner_block_id:
            block = PlannerBlock.query.filter_by(id=planner_block_id, user_id=user_id).first()
            if not block:
                raise NotFoundException("Planner block not found or unauthorized")

        # Automatically pause/complete any existing active sessions
        active_sessions = FocusSession.query.filter_by(user_id=user_id, status="active").all()
        now_utc = datetime.now(timezone.utc)
        for s in active_sessions:
            s.status = "paused"
            s.paused_at = now_utc

        new_session = FocusSession(
            user_id=user_id,
            task_id=task_id,
            planner_block_id=planner_block_id,
            title=title or "Focus Session",
            session_type=session_type,
            target_duration_minutes=target_duration_minutes,
            actual_duration_seconds=0,
            status="active",
            start_time=now_utc,
            notes=notes
        )
        db.session.add(new_session)
        db.session.commit()
        return new_session

    def pause_session(self, user_id: str, session_id: str) -> FocusSession:
        session = FocusSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise NotFoundException("Focus session not found")
        if session.status != "active":
            raise BadRequestException("Can only pause an active session")

        now_utc = datetime.now(timezone.utc)
        # Calculate elapsed seconds since start or last resume
        session.status = "paused"
        session.paused_at = now_utc
        db.session.commit()
        return session

    def resume_session(self, user_id: str, session_id: str) -> FocusSession:
        session = FocusSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise NotFoundException("Focus session not found")
        if session.status != "paused":
            raise BadRequestException("Can only resume a paused session")

        session.status = "active"
        session.paused_at = None
        db.session.commit()
        return session

    def stop_session(
        self,
        user_id: str,
        session_id: str,
        actual_duration_seconds: int,
        status: str = "completed",
        notes: Optional[str] = None
    ) -> FocusSession:
        session = FocusSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise NotFoundException("Focus session not found")

        now_utc = datetime.now(timezone.utc)
        session.end_time = now_utc
        session.status = status if status in ["completed", "cancelled"] else "completed"
        session.actual_duration_seconds = max(0, actual_duration_seconds)
        if notes:
            session.notes = notes
        db.session.commit()
        return session

    def log_distraction(
        self,
        user_id: str,
        session_id: str,
        distraction_type: str,
        description: str
    ) -> FocusDistraction:
        session = FocusSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise NotFoundException("Focus session not found")

        distraction = FocusDistraction(
            focus_session_id=session_id,
            user_id=user_id,
            distraction_type=distraction_type,
            description=description,
            logged_at=datetime.now(timezone.utc)
        )
        db.session.add(distraction)
        db.session.commit()
        return distraction

    def get_active_session(self, user_id: str) -> Optional[FocusSession]:
        return FocusSession.query.filter(
            FocusSession.user_id == user_id,
            FocusSession.status.in_(["active", "paused"])
        ).order_by(FocusSession.start_time.desc()).first()

    def list_sessions(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20,
        session_type: Optional[str] = None
    ) -> Tuple[List[FocusSession], Dict[str, Any]]:
        query = FocusSession.query.filter_by(user_id=user_id)
        if session_type:
            query = query.filter_by(session_type=session_type)
        
        total = query.count()
        sessions = query.order_by(FocusSession.start_time.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return sessions, {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if per_page else 1
        }

    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc)
        today_start = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)
        week_start = today_start - timedelta(days=now_utc.weekday())

        goal = self.get_or_create_goal(user_id)

        # Work sessions today
        today_sessions = FocusSession.query.filter(
            FocusSession.user_id == user_id,
            FocusSession.session_type == "work",
            FocusSession.start_time >= today_start,
            FocusSession.status == "completed"
        ).all()
        today_seconds = sum(s.actual_duration_seconds for s in today_sessions)
        today_minutes = round(today_seconds / 60, 1)

        # Work sessions this week
        week_sessions = FocusSession.query.filter(
            FocusSession.user_id == user_id,
            FocusSession.session_type == "work",
            FocusSession.start_time >= week_start,
            FocusSession.status == "completed"
        ).all()
        week_seconds = sum(s.actual_duration_seconds for s in week_sessions)
        week_minutes = round(week_seconds / 60, 1)

        # Lifetime total
        all_completed = FocusSession.query.filter(
            FocusSession.user_id == user_id,
            FocusSession.session_type == "work",
            FocusSession.status == "completed"
        ).all()
        total_seconds = sum(s.actual_duration_seconds for s in all_completed)
        total_hours = round(total_seconds / 3600, 2)

        # Distractions count today
        distractions_count = FocusDistraction.query.filter(
            FocusDistraction.user_id == user_id,
            FocusDistraction.logged_at >= today_start
        ).count()

        return {
            "today_minutes": today_minutes,
            "today_target_minutes": goal.daily_target_minutes,
            "today_progress_pct": min(100.0, round((today_minutes / goal.daily_target_minutes * 100), 1)) if goal.daily_target_minutes > 0 else 0,
            "week_minutes": week_minutes,
            "week_target_minutes": goal.weekly_target_minutes,
            "week_progress_pct": min(100.0, round((week_minutes / goal.weekly_target_minutes * 100), 1)) if goal.weekly_target_minutes > 0 else 0,
            "total_focused_hours": total_hours,
            "completed_sessions_today": len(today_sessions),
            "distractions_logged_today": distractions_count,
            "goal": goal.to_dict()
        }

