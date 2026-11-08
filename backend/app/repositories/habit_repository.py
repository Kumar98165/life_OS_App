"""LifeOS - Habit Repository.

Handles database persistence, queries, check-in log transactions,
and streak calculation algorithms for daily, weekday, and weekly habits.
"""
from datetime import date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import desc, asc, func, and_
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.habit import Habit, HabitLog


def _get_previous_scheduled_day(d: date, frequency: str) -> date:
    """Return the scheduled calendar day immediately prior to date d."""
    if frequency == "weekdays":
        # If Monday (0), previous scheduled day was Friday (-3 days)
        # If Sunday (6), previous scheduled day was Friday (-2 days)
        # If Saturday (5), previous scheduled day was Friday (-1 day)
        # Otherwise -1 day
        weekday = d.weekday()
        if weekday == 0:
            return d - timedelta(days=3)
        elif weekday == 6:
            return d - timedelta(days=2)
        elif weekday == 5:
            return d - timedelta(days=1)
        else:
            return d - timedelta(days=1)
    # Default daily
    return d - timedelta(days=1)


def _is_day_scheduled(d: date, frequency: str) -> bool:
    """Check if the given calendar date is a scheduled day for the frequency."""
    if frequency == "weekdays":
        return d.weekday() < 5
    return True  # daily and weekly are valid on any day


class HabitRepository:
    """Repository handling database operations and streak mechanics for habits."""

    def create_habit(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        frequency: str = "daily",
        target_days_per_week: int = 7,
        color_hex: str = "#6C63FF",
        icon: Optional[str] = None
    ) -> Habit:
        """Create and persist a new habit."""
        habit = Habit(
            user_id=user_id,
            title=title,
            description=description,
            frequency=frequency,
            target_days_per_week=target_days_per_week,
            color_hex=color_hex,
            icon=icon,
            current_streak=0,
            longest_streak=0,
            is_archived=False
        )
        db.session.add(habit)
        db.session.commit()
        return habit

    def get_by_id(self, habit_id: str) -> Optional[Habit]:
        """Retrieve habit by ID with eager-loaded logs."""
        return (
            Habit.query
            .options(selectinload(Habit.logs))
            .filter_by(id=habit_id)
            .first()
        )

    def list_for_user(
        self,
        user_id: str,
        include_archived: bool = False,
        frequency: Optional[str] = None
    ) -> List[Habit]:
        """List habits belonging to user, optionally filtering by frequency or archived."""
        query = Habit.query.options(selectinload(Habit.logs)).filter_by(user_id=user_id)
        if not include_archived:
            query = query.filter_by(is_archived=False)
        if frequency:
            query = query.filter_by(frequency=frequency)
        return query.order_by(Habit.created_at.desc()).all()

    def update_habit(self, habit: Habit, data: Dict[str, Any]) -> Habit:
        """Update fields of an existing habit."""
        for field, value in data.items():
            if hasattr(habit, field):
                setattr(habit, field, value)
        db.session.commit()
        return habit

    def delete_habit(self, habit: Habit) -> None:
        """Permanently delete a habit and cascade-delete its logs."""
        db.session.delete(habit)
        db.session.commit()

    def get_log_by_id(self, log_id: str) -> Optional[HabitLog]:
        """Retrieve a habit log by ID."""
        return HabitLog.query.filter_by(id=log_id).first()

    def get_log(self, habit_id: str, log_date: date) -> Optional[HabitLog]:
        """Retrieve log for a specific habit on a specific date."""
        return HabitLog.query.filter_by(habit_id=habit_id, log_date=log_date).first()

    def log_check_in(
        self,
        habit: Habit,
        log_date: date,
        completed: bool = True,
        notes: Optional[str] = None
    ) -> HabitLog:
        """Record or update a check-in log and recompute streaks atomically."""
        existing_log = self.get_log(habit.id, log_date)
        if existing_log:
            existing_log.completed = completed
            if notes is not None:
                existing_log.notes = notes
            log = existing_log
        else:
            log = HabitLog(
                habit_id=habit.id,
                log_date=log_date,
                completed=completed,
                notes=notes
            )
            db.session.add(log)

        db.session.flush()

        # Recalculate streak values and update habit
        stats = self.calculate_streaks(habit, reference_date=date.today())
        habit.current_streak = stats["current_streak"]
        habit.longest_streak = max(habit.longest_streak, stats["longest_streak"])

        db.session.commit()
        return log

    def delete_log(self, habit: Habit, log: HabitLog) -> None:
        """Undo a check-in and recompute streaks."""
        db.session.delete(log)
        db.session.flush()

        # Recalculate streaks
        stats = self.calculate_streaks(habit, reference_date=date.today())
        habit.current_streak = stats["current_streak"]
        habit.longest_streak = stats["longest_streak"]

        db.session.commit()

    def get_habit_logs(
        self,
        habit_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[HabitLog]:
        """Retrieve historical logs for a habit within an optional date range."""
        query = HabitLog.query.filter_by(habit_id=habit_id)
        if start_date:
            query = query.filter(HabitLog.log_date >= start_date)
        if end_date:
            query = query.filter(HabitLog.log_date <= end_date)
        return query.order_by(HabitLog.log_date.desc()).limit(limit).all()

    def calculate_streaks(
        self,
        habit: Habit,
        reference_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Compute current streak, longest streak, consistency, and completion rates.

        Handles daily, weekday-only, and weekly target recurrence without breaking
        streaks prematurely before today has finished.
        """
        ref_date = reference_date or date.today()
        # Query all completed log dates
        completed_logs = (
            HabitLog.query
            .filter(
                HabitLog.habit_id == habit.id,
                HabitLog.completed.is_(True),
                HabitLog.log_date <= ref_date
            )
            .order_by(HabitLog.log_date.asc())
            .all()
        )
        completed_dates = {log.log_date for log in completed_logs}
        total_completed = len(completed_dates)

        frequency = habit.frequency or "daily"

        # --- Current Streak Calculation ---
        current_streak = 0
        if frequency == "weekdays":
            current_streak = self._calculate_weekdays_current_streak(completed_dates, ref_date)
            longest_streak = self._calculate_weekdays_longest_streak(completed_dates)
        elif frequency == "weekly":
            current_streak, longest_streak = self._calculate_weekly_streaks(
                completed_dates, habit.target_days_per_week, ref_date
            )
        else:  # daily
            current_streak = self._calculate_daily_current_streak(completed_dates, ref_date)
            longest_streak = self._calculate_daily_longest_streak(completed_dates)

        longest_streak = max(longest_streak, current_streak, habit.longest_streak)

        # --- Consistency and Completion Rates ---
        # 1. 30-day window
        window_start = ref_date - timedelta(days=29)
        completed_in_window = sum(1 for d in completed_dates if window_start <= d <= ref_date)
        scheduled_in_window = 0
        cur = window_start
        while cur <= ref_date:
            if _is_day_scheduled(cur, frequency):
                scheduled_in_window += 1
            cur += timedelta(days=1)

        monthly_consistency = round(
            (completed_in_window / scheduled_in_window * 100.0) if scheduled_in_window > 0 else 0.0,
            1
        )

        # 2. 7-day window
        week_start_7 = ref_date - timedelta(days=6)
        completed_in_7 = sum(1 for d in completed_dates if week_start_7 <= d <= ref_date)
        scheduled_in_7 = 0
        cur = week_start_7
        while cur <= ref_date:
            if _is_day_scheduled(cur, frequency):
                scheduled_in_7 += 1
            cur += timedelta(days=1)

        weekly_consistency = round(
            (completed_in_7 / scheduled_in_7 * 100.0) if scheduled_in_7 > 0 else 0.0,
            1
        )

        # 3. Overall completion rate from habit creation or first log
        creation_date = habit.created_at.date() if habit.created_at else ref_date
        total_scheduled = 0
        cur = creation_date
        while cur <= ref_date:
            if _is_day_scheduled(cur, frequency):
                total_scheduled += 1
            cur += timedelta(days=1)

        if total_scheduled == 0:
            total_scheduled = 1

        completion_rate = round(min(100.0, (total_completed / total_scheduled) * 100.0), 1)

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_completed_days": total_completed,
            "completion_rate": completion_rate,
            "weekly_consistency": weekly_consistency,
            "monthly_consistency": monthly_consistency,
        }

    # Helper streak algorithms:
    @staticmethod
    def _calculate_daily_current_streak(completed_dates: set[date], ref_date: date) -> int:
        """Daily streak: if today is incomplete, streak remains alive if yesterday was completed."""
        streak = 0
        check_date = ref_date

        if ref_date in completed_dates:
            streak += 1
            check_date = ref_date - timedelta(days=1)
        else:
            # Check yesterday; if missed, current streak is 0
            yesterday = ref_date - timedelta(days=1)
            if yesterday in completed_dates:
                streak += 1
                check_date = yesterday - timedelta(days=1)
            else:
                return 0

        while check_date in completed_dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    @staticmethod
    def _calculate_daily_longest_streak(completed_dates: set[date]) -> int:
        """Find max consecutive calendar days with completed logs."""
        if not completed_dates:
            return 0
        sorted_dates = sorted(completed_dates)
        max_streak = 1
        current = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
                current += 1
                max_streak = max(max_streak, current)
            elif sorted_dates[i] > sorted_dates[i - 1] + timedelta(days=1):
                current = 1
        return max_streak

    @staticmethod
    def _calculate_weekdays_current_streak(completed_dates: set[date], ref_date: date) -> int:
        """Weekday streak (Mon-Fri). Weekends do not break streak."""
        streak = 0
        is_weekday = ref_date.weekday() < 5

        if is_weekday:
            if ref_date in completed_dates:
                streak += 1
                check_date = _get_previous_scheduled_day(ref_date, "weekdays")
            else:
                prev_sched = _get_previous_scheduled_day(ref_date, "weekdays")
                if prev_sched in completed_dates:
                    streak += 1
                    check_date = _get_previous_scheduled_day(prev_sched, "weekdays")
                else:
                    return 0
        else:
            # ref_date is Saturday or Sunday -> last scheduled day was Friday
            last_friday = ref_date - timedelta(days=(ref_date.weekday() - 4))
            if last_friday in completed_dates:
                streak += 1
                check_date = _get_previous_scheduled_day(last_friday, "weekdays")
            else:
                return 0

        while check_date in completed_dates:
            streak += 1
            check_date = _get_previous_scheduled_day(check_date, "weekdays")

        return streak

    @staticmethod
    def _calculate_weekdays_longest_streak(completed_dates: set[date]) -> int:
        """Find max consecutive scheduled weekdays completed."""
        weekday_dates = sorted([d for d in completed_dates if d.weekday() < 5])
        if not weekday_dates:
            return 0
        max_streak = 1
        current = 1
        for i in range(1, len(weekday_dates)):
            prev = weekday_dates[i - 1]
            curr = weekday_dates[i]
            # Consecutive if difference is 1 day (Mon-Fri) or 3 days (Fri to Mon)
            if (curr == prev + timedelta(days=1)) or (prev.weekday() == 4 and curr == prev + timedelta(days=3)):
                current += 1
                max_streak = max(max_streak, current)
            else:
                current = 1
        return max_streak

    @staticmethod
    def _calculate_weekly_streaks(
        completed_dates: set[date],
        target_days: int,
        ref_date: date
    ) -> Tuple[int, int]:
        """Weekly streak: consecutive calendar weeks meeting the target_days requirement."""
        if not completed_dates:
            return 0, 0

        # Group completed dates by week start (Monday)
        from collections import defaultdict
        week_counts: dict[date, int] = defaultdict(int)
        for d in completed_dates:
            mon = d - timedelta(days=d.weekday())
            week_counts[mon] += 1

        current_mon = ref_date - timedelta(days=ref_date.weekday())

        # Check current streak
        streak = 0
        check_mon = current_mon
        if week_counts.get(current_mon, 0) >= target_days:
            streak += 1
            check_mon = current_mon - timedelta(days=7)
        else:
            # Current week not yet met: alive if last week met
            prev_mon = current_mon - timedelta(days=7)
            if week_counts.get(prev_mon, 0) >= target_days:
                streak += 1
                check_mon = prev_mon - timedelta(days=7)
            else:
                streak = 0
                check_mon = None

        if check_mon:
            while week_counts.get(check_mon, 0) >= target_days:
                streak += 1
                check_mon -= timedelta(days=7)

        # Longest streak
        all_mondays = sorted(week_counts.keys())
        successful_weeks = {m for m in all_mondays if week_counts[m] >= target_days}
        longest = 0
        curr_run = 0
        if successful_weeks:
            sorted_success = sorted(successful_weeks)
            longest = 1
            curr_run = 1
            for i in range(1, len(sorted_success)):
                if sorted_success[i] == sorted_success[i - 1] + timedelta(days=7):
                    curr_run += 1
                    longest = max(longest, curr_run)
                else:
                    curr_run = 1

        return streak, max(longest, streak)

    def get_daily_summary(self, user_id: str, target_date: date) -> Dict[str, Any]:
        """Return daily completion summary for all active habits of user on target_date."""
        habits = self.list_for_user(user_id=user_id, include_archived=False)
        is_target_weekday = target_date.weekday() < 5

        scheduled_habits = []
        completed_habits = []

        # Get all logs on this date for the user's habits
        habit_ids = [h.id for h in habits]
        logs_map = {}
        if habit_ids:
            logs = HabitLog.query.filter(
                HabitLog.habit_id.in_(habit_ids),
                HabitLog.log_date == target_date
            ).all()
            logs_map = {l.habit_id: l for l in logs}

        for habit in habits:
            # Check if scheduled today
            freq = habit.frequency or "daily"
            is_scheduled = True
            if freq == "weekdays" and not is_target_weekday:
                is_scheduled = False

            log = logs_map.get(habit.id)
            is_completed = bool(log and log.completed)

            habit_data = habit.to_dict()
            habit_data["completed_today"] = is_completed
            habit_data["log_id"] = log.id if log else None
            habit_data["is_scheduled"] = is_scheduled

            if is_scheduled:
                scheduled_habits.append(habit_data)
                if is_completed:
                    completed_habits.append(habit_data)
            elif is_completed:
                # If marked on an unscheduled day, still track as completed
                completed_habits.append(habit_data)

        scheduled_count = len(scheduled_habits)
        completed_count = len(completed_habits)
        completion_percent = round(
            (completed_count / scheduled_count * 100.0) if scheduled_count > 0 else 0.0,
            1
        )

        return {
            "date": target_date.isoformat(),
            "scheduled_count": scheduled_count,
            "completed_count": completed_count,
            "completion_percentage": completion_percent,
            "habits": scheduled_habits,
        }

    def get_weekly_summary(self, user_id: str, week_start: date) -> Dict[str, Any]:
        """Return summary of 7 days starting from week_start (Monday)."""
        days = []
        total_completed = 0
        total_scheduled = 0

        for i in range(7):
            d = week_start + timedelta(days=i)
            day_sum = self.get_daily_summary(user_id, d)
            total_completed += day_sum["completed_count"]
            total_scheduled += day_sum["scheduled_count"]
            days.append({
                "date": d.isoformat(),
                "day_name": d.strftime("%a"),
                "scheduled_count": day_sum["scheduled_count"],
                "completed_count": day_sum["completed_count"],
                "completion_percentage": day_sum["completion_percentage"]
            })

        overall_percentage = round(
            (total_completed / total_scheduled * 100.0) if total_scheduled > 0 else 0.0,
            1
        )

        return {
            "week_start": week_start.isoformat(),
            "week_end": (week_start + timedelta(days=6)).isoformat(),
            "total_completed": total_completed,
            "total_scheduled": total_scheduled,
            "overall_percentage": overall_percentage,
            "days": days
        }

    def get_monthly_summary(self, user_id: str, year: int, month: int) -> Dict[str, Any]:
        """Return completion counts and rate for each day in a given month."""
        import calendar
        num_days = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)

        habits = self.list_for_user(user_id=user_id, include_archived=False)
        habit_ids = [h.id for h in habits]

        # Fetch all completed logs in month
        logs_count_by_date = {}
        if habit_ids:
            results = (
                db.session.query(HabitLog.log_date, func.count(HabitLog.id))
                .filter(
                    HabitLog.habit_id.in_(habit_ids),
                    HabitLog.completed.is_(True),
                    HabitLog.log_date >= start_date,
                    HabitLog.log_date <= end_date
                )
                .group_by(HabitLog.log_date)
                .all()
            )
            logs_count_by_date = {r[0]: r[1] for r in results}

        days_summary = []
        month_completed = 0
        month_scheduled = 0

        for day in range(1, num_days + 1):
            d = date(year, month, day)
            completed_count = logs_count_by_date.get(d, 0)
            is_wkday = d.weekday() < 5
            scheduled_count = sum(
                1 for h in habits
                if (h.frequency != "weekdays" or is_wkday)
            )

            month_completed += completed_count
            month_scheduled += scheduled_count

            rate = round(
                (completed_count / scheduled_count * 100.0) if scheduled_count > 0 else 0.0,
                1
            )
            days_summary.append({
                "date": d.isoformat(),
                "day": day,
                "completed_count": completed_count,
                "scheduled_count": scheduled_count,
                "completion_percentage": rate
            })

        overall_percentage = round(
            (month_completed / month_scheduled * 100.0) if month_scheduled > 0 else 0.0,
            1
        )

        return {
            "year": year,
            "month": month,
            "total_habits": len(habits),
            "total_completed": month_completed,
            "total_scheduled": month_scheduled,
            "overall_percentage": overall_percentage,
            "days": days_summary
        }

