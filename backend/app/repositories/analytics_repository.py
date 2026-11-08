from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, func, and_, or_, case
from app import db
from app.models.task import Task
from app.models.planner import PlannerBlock
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal, GoalMilestone
from app.models.finance import FinancialTransaction, FinancialCategory, Budget, SavingsGoal


class AnalyticsRepository:
    """PostgreSQL data aggregation repository for LifeOS analytics."""

    # -------------------------------------------------------------------------
    # Productivity (Tasks & Planner)
    # -------------------------------------------------------------------------

    def get_task_metrics(
        self,
        user_id: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> Dict[str, Any]:
        """Aggregate task metrics and daily completion velocity."""
        now = datetime.now(timezone.utc)

        # 1. Total tasks created in period
        created_count = db.session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.created_at.between(start_dt, end_dt)
            )
        ).scalar() or 0

        # 2. Tasks completed in period
        completed_count = db.session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.status == "completed",
                or_(
                    Task.completed_at.between(start_dt, end_dt),
                    and_(Task.completed_at.is_(None), Task.created_at.between(start_dt, end_dt))
                )
            )
        ).scalar() or 0

        # 3. Active pending tasks
        pending_count = db.session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.status.in_(["pending", "in_progress", "todo"])
            )
        ).scalar() or 0

        # 4. Overdue tasks
        overdue_count = db.session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.status != "completed",
                Task.due_date < now
            )
        ).scalar() or 0

        # 5. Completion percentage
        eligible_tasks = completed_count + pending_count
        completion_pct = (
            round((completed_count / eligible_tasks) * 100, 1)
            if eligible_tasks > 0 else 100.0
        )

        # 6. Daily task completion trend
        trend_stmt = (
            select(
                func.coalesce(func.date(Task.completed_at), func.date(Task.created_at)).label("day"),
                func.count(Task.id).label("count")
            )
            .where(
                Task.user_id == user_id,
                Task.status == "completed",
                or_(
                    Task.completed_at.between(start_dt, end_dt),
                    and_(Task.completed_at.is_(None), Task.created_at.between(start_dt, end_dt))
                )
            )
            .group_by(func.coalesce(func.date(Task.completed_at), func.date(Task.created_at)))
            .order_by("day")
        )
        trend_rows = db.session.execute(trend_stmt).all()
        trend_map = {str(r.day): r.count for r in trend_rows}

        # Build full date series
        current = start_dt.date()
        end_d = end_dt.date()
        daily_trend = []
        while current <= end_d:
            d_str = current.isoformat()
            daily_trend.append({"date": d_str, "completed": trend_map.get(d_str, 0)})
            current += timedelta(days=1)

        return {
            "total_tasks": created_count,
            "completed_tasks": completed_count,
            "pending_tasks": pending_count,
            "overdue_tasks": overdue_count,
            "completion_percentage": completion_pct,
            "daily_completion_trend": daily_trend,
        }

    def get_planner_metrics(
        self,
        user_id: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> Dict[str, Any]:
        """Aggregate planner blocks by completion and type distribution."""
        total_blocks = db.session.execute(
            select(func.count(PlannerBlock.id)).where(
                PlannerBlock.user_id == user_id,
                PlannerBlock.start_time.between(start_dt, end_dt)
            )
        ).scalar() or 0

        completed_blocks = db.session.execute(
            select(func.count(PlannerBlock.id)).where(
                PlannerBlock.user_id == user_id,
                PlannerBlock.status == "completed",
                PlannerBlock.start_time.between(start_dt, end_dt)
            )
        ).scalar() or 0

        completion_pct = (
            round((completed_blocks / total_blocks) * 100, 1)
            if total_blocks > 0 else 100.0
        )

        # Activity Distribution
        dist_stmt = (
            select(
                PlannerBlock.block_type,
                func.count(PlannerBlock.id).label("count")
            )
            .where(
                PlannerBlock.user_id == user_id,
                PlannerBlock.start_time.between(start_dt, end_dt)
            )
            .group_by(PlannerBlock.block_type)
        )
        dist_rows = db.session.execute(dist_stmt).all()
        distribution = [
            {"type": r.block_type, "count": r.count}
            for r in dist_rows
        ]

        return {
            "total_planner_blocks": total_blocks,
            "completed_planner_blocks": completed_blocks,
            "planner_completion_percentage": completion_pct,
            "planner_distribution": distribution,
        }

    # -------------------------------------------------------------------------
    # Habits & Streaks
    # -------------------------------------------------------------------------

    def get_habit_metrics(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Compute habit consistency, streaks, and scheduled check-in rates."""
        habits = list(
            db.session.execute(
                select(Habit).where(
                    Habit.user_id == user_id,
                    Habit.is_archived.is_(False)
                )
            ).scalars().all()
        )

        if not habits:
            return {
                "total_active_habits": 0,
                "total_scheduled_checkins": 0,
                "total_completed_checkins": 0,
                "consistency_percentage": 100.0,
                "average_current_streak": 0.0,
                "best_streak_record": 0,
                "habits_performance": [],
                "daily_trend": [],
            }

        habit_ids = [h.id for h in habits]

        # Fetch logs in range
        logs = list(
            db.session.execute(
                select(HabitLog).where(
                    HabitLog.habit_id.in_(habit_ids),
                    HabitLog.log_date.between(start_date, end_date),
                    HabitLog.completed.is_(True)
                )
            ).scalars().all()
        )

        completed_by_habit: Dict[str, int] = {}
        completed_by_date: Dict[str, int] = {}

        for l in logs:
            completed_by_habit[l.habit_id] = completed_by_habit.get(l.habit_id, 0) + 1
            d_str = l.log_date.isoformat()
            completed_by_date[d_str] = completed_by_date.get(d_str, 0) + 1

        total_scheduled = 0
        total_completed = len(logs)
        habits_perf = []

        total_days = (end_date - start_date).days + 1

        for h in habits:
            scheduled_for_h = 0
            curr = start_date
            while curr <= end_date:
                weekday = curr.weekday()
                if h.frequency == "daily":
                    scheduled_for_h += 1
                elif h.frequency == "weekdays":
                    if weekday < 5:
                        scheduled_for_h += 1
                elif h.frequency == "weekly":
                    # Pro-rated target days
                    scheduled_for_h += max(1, h.target_days_per_week // 7)
                curr += timedelta(days=1)

            scheduled_for_h = max(scheduled_for_h, 1)
            comp_h = completed_by_habit.get(h.id, 0)
            total_scheduled += scheduled_for_h

            rate_h = min(100.0, round((comp_h / scheduled_for_h) * 100, 1))

            habits_perf.append({
                "id": h.id,
                "title": h.title,
                "color_hex": h.color_hex,
                "frequency": h.frequency,
                "current_streak": h.current_streak,
                "best_streak": h.longest_streak,
                "completed_in_period": comp_h,
                "scheduled_in_period": scheduled_for_h,
                "completion_percentage": rate_h,
            })

        consistency_pct = (
            min(100.0, round((total_completed / total_scheduled) * 100, 1))
            if total_scheduled > 0 else 100.0
        )

        avg_streak = round(sum(h.current_streak for h in habits) / len(habits), 1)
        best_record = max(h.longest_streak for h in habits)

        # Build date series
        curr = start_date
        daily_trend = []
        while curr <= end_date:
            d_str = curr.isoformat()
            daily_trend.append({"date": d_str, "completed": completed_by_date.get(d_str, 0)})
            curr += timedelta(days=1)

        return {
            "total_active_habits": len(habits),
            "total_scheduled_checkins": total_scheduled,
            "total_completed_checkins": total_completed,
            "consistency_percentage": consistency_pct,
            "average_current_streak": avg_streak,
            "best_streak_record": best_record,
            "habits_performance": habits_perf,
            "daily_trend": daily_trend,
        }

    # -------------------------------------------------------------------------
    # Goals & Milestones
    # -------------------------------------------------------------------------

    def get_goal_metrics(self, user_id: str) -> Dict[str, Any]:
        """Aggregate goals, progress distributions, and milestone completion."""
        now = datetime.now(timezone.utc)

        goals = list(
            db.session.execute(
                select(Goal).where(
                    Goal.user_id == user_id,
                    Goal.status != "cancelled"
                )
            ).scalars().all()
        )

        total_goals = len(goals)
        completed_goals = sum(1 for g in goals if g.status == "completed")
        active_goals = total_goals - completed_goals
        completion_pct = round((completed_goals / total_goals) * 100, 1) if total_goals > 0 else 100.0

        # Milestones
        milestone_stmt = (
            select(
                func.count(GoalMilestone.id).label("total"),
                func.count(case((GoalMilestone.is_completed.is_(True), 1))).label("completed")
            )
            .join(Goal, GoalMilestone.goal_id == Goal.id)
            .where(
                Goal.user_id == user_id,
                Goal.status != "cancelled"
            )
        )
        milestone_res = db.session.execute(milestone_stmt).one()
        total_m = milestone_res.total or 0
        comp_m = milestone_res.completed or 0
        milestone_pct = round((comp_m / total_m) * 100, 1) if total_m > 0 else 100.0

        goals_prog = []
        upcoming_deadlines = []

        for g in goals:
            goals_prog.append({
                "id": g.id,
                "title": g.title,
                "category": g.category,
                "progress_percentage": round(g.progress_percent, 1),
                "status": g.status,
                "target_date": g.target_date.isoformat() if g.target_date else None,
            })

            if g.target_date and g.status != "completed":
                target_dt = g.target_date if g.target_date.tzinfo else g.target_date.replace(tzinfo=timezone.utc)
                is_overdue = target_dt < now
                days_diff = (target_dt - now).days
                if is_overdue or days_diff <= 30:
                    upcoming_deadlines.append({
                        "id": g.id,
                        "title": g.title,
                        "target_date": g.target_date.isoformat(),
                        "days_remaining": days_diff,
                        "is_overdue": is_overdue,
                    })

        upcoming_deadlines.sort(key=lambda x: x["days_remaining"])

        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "completion_percentage": completion_pct,
            "total_milestones": total_m,
            "completed_milestones": comp_m,
            "milestone_completion_percentage": milestone_pct,
            "goals_progress": goals_prog,
            "upcoming_deadlines": upcoming_deadlines,
        }

    # -------------------------------------------------------------------------
    # Financial Analytics
    # -------------------------------------------------------------------------

    def get_financial_metrics(
        self,
        user_id: str,
        start_dt: datetime,
        end_dt: datetime,
        month_str: str
    ) -> Dict[str, Any]:
        """Aggregate income, expenses, category distribution, and budget adherence."""
        txs = list(
            db.session.execute(
                select(FinancialTransaction).where(
                    FinancialTransaction.user_id == user_id,
                    FinancialTransaction.is_deleted.is_(False),
                    FinancialTransaction.transaction_date.between(start_dt, end_dt)
                )
            ).scalars().all()
        )

        income = sum((t.amount for t in txs if t.transaction_type == "income"), start=Decimal("0.00")).quantize(Decimal("0.01"))
        expense = sum((t.amount for t in txs if t.transaction_type == "expense"), start=Decimal("0.00")).quantize(Decimal("0.01"))
        net_savings = (income - expense).quantize(Decimal("0.01"))

        savings_rate = 0.0
        if income > 0 and net_savings > 0:
            savings_rate = float(round((net_savings / income) * 100, 1))

        # Spending by category
        cat_map: Dict[str, Decimal] = {}
        for t in txs:
            if t.transaction_type == "expense":
                cid = t.category_id or "uncategorized"
                cat_map[cid] = cat_map.get(cid, Decimal("0.00")) + t.amount

        categories = {
            c.id: c
            for c in db.session.execute(
                select(FinancialCategory).where(
                    or_(FinancialCategory.user_id == user_id, FinancialCategory.is_system.is_(True))
                )
            ).scalars().all()
        }

        category_breakdown = []
        for cid, amount in cat_map.items():
            cat_obj = categories.get(cid)
            name = cat_obj.name if cat_obj else "Uncategorized"
            color = cat_obj.color_hex if cat_obj else "#6C63FF"
            pct = float(round((amount / expense) * 100, 1)) if expense > 0 else 0.0
            category_breakdown.append({
                "category_id": cid,
                "name": name,
                "color_hex": color,
                "amount": str(amount.quantize(Decimal("0.01"))),
                "percentage": pct,
            })

        category_breakdown.sort(key=lambda x: float(x["amount"]), reverse=True)

        # Budget adherence for current month
        budgets = list(
            db.session.execute(
                select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.month == month_str
                )
            ).scalars().all()
        )

        over_budget_count = 0
        for b in budgets:
            if b.category_id:
                spent = sum((t.amount for t in txs if t.category_id == b.category_id and t.transaction_type == "expense"), start=Decimal("0.00"))
            else:
                spent = expense
            if spent > b.amount:
                over_budget_count += 1

        budget_adherence = (
            round(((len(budgets) - over_budget_count) / len(budgets)) * 100, 1)
            if budgets else 100.0
        )

        # Savings Goals Progress
        savings_goals = list(
            db.session.execute(
                select(SavingsGoal).where(
                    SavingsGoal.user_id == user_id,
                    SavingsGoal.status != "archived"
                )
            ).scalars().all()
        )
        goals_data = [
            {
                "id": sg.id,
                "title": sg.title,
                "target_amount": str(sg.target_amount),
                "current_amount": str(sg.current_amount),
                "progress_percentage": min(100.0, float(round((sg.current_amount / sg.target_amount) * 100, 1))) if sg.target_amount > 0 else 0.0,
                "status": sg.status,
            }
            for sg in savings_goals
        ]

        return {
            "period": month_str,
            "total_income": str(income),
            "total_expenses": str(expense),
            "net_savings": str(net_savings),
            "savings_rate": savings_rate,
            "spending_by_category": category_breakdown,
            "budget_adherence_percentage": budget_adherence,
            "savings_goals_progress": goals_data,
        }
