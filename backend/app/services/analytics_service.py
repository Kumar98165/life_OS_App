import json
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple
from zoneinfo import ZoneInfo
from app.repositories.analytics_repository import AnalyticsRepository
from app.models.user_preference import UserPreference
from app import db
from app.ai.config import get_llm
from langchain_core.messages import SystemMessage, HumanMessage


class AnalyticsService:
    """Business logic for LifeOS analytics, Life Score calculation, and AI insights."""

    def __init__(self, repo: Optional[AnalyticsRepository] = None):
        self.repo = repo or AnalyticsRepository()

    # -------------------------------------------------------------------------
    # Date Range & Timezone Parsing
    # -------------------------------------------------------------------------

    def resolve_date_window(
        self,
        user_id: str,
        period: str = "week",
        start_date_str: Optional[str] = None,
        end_date_str: Optional[str] = None,
        tz_override: Optional[str] = None,
    ) -> Tuple[datetime, datetime, date, date, str]:
        """Convert period and timezone into UTC start/end datetimes and local dates."""
        tz_name = tz_override
        if not tz_name:
            pref = db.session.execute(
                db.select(UserPreference).where(UserPreference.user_id == user_id)
            ).scalar_one_or_none()
            tz_name = pref.timezone if pref else "UTC"

        try:
            user_tz = ZoneInfo(tz_name)
        except Exception:
            user_tz = timezone.utc

        now_local = datetime.now(user_tz)
        today_local = now_local.date()

        if period == "day":
            start_d = today_local
            end_d = today_local
        elif period == "week":
            # Last 7 days
            start_d = today_local - timedelta(days=6)
            end_d = today_local
        elif period == "month":
            # Current calendar month
            start_d = date(today_local.year, today_local.month, 1)
            end_d = today_local
        elif period == "year":
            # Current calendar year
            start_d = date(today_local.year, 1, 1)
            end_d = today_local
        elif period == "custom" and start_date_str and end_date_str:
            start_d = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_d = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if start_d > end_d:
                start_d, end_d = end_d, start_d
            # Enforce max 365 days
            if (end_d - start_d).days > 365:
                end_d = start_d + timedelta(days=365)
        else:
            # Default to last 7 days
            start_d = today_local - timedelta(days=6)
            end_d = today_local

        # Convert local midnight to UTC
        start_local_dt = datetime(start_d.year, start_d.month, start_d.day, 0, 0, 0, tzinfo=user_tz)
        end_local_dt = datetime(end_d.year, end_d.month, end_d.day, 23, 59, 59, tzinfo=user_tz)

        start_utc = start_local_dt.astimezone(timezone.utc)
        end_utc = end_local_dt.astimezone(timezone.utc)

        return start_utc, end_utc, start_d, end_d, tz_name

    # -------------------------------------------------------------------------
    # Core Domain Analytics
    # -------------------------------------------------------------------------

    def get_productivity_analytics(self, user_id: str, period: str = "week", **kwargs) -> Dict[str, Any]:
        """Aggregate productivity metrics across Tasks and Planner."""
        start_utc, end_utc, _, _, _ = self.resolve_date_window(user_id, period, kwargs.get("start_date"), kwargs.get("end_date"), kwargs.get("timezone"))
        task_data = self.repo.get_task_metrics(user_id, start_utc, end_utc)
        planner_data = self.repo.get_planner_metrics(user_id, start_utc, end_utc)

        return {**task_data, **planner_data}

    def get_habit_analytics(self, user_id: str, period: str = "week", **kwargs) -> Dict[str, Any]:
        """Aggregate habit consistency and streak progression."""
        _, _, start_d, end_d, _ = self.resolve_date_window(user_id, period, kwargs.get("start_date"), kwargs.get("end_date"), kwargs.get("timezone"))
        return self.repo.get_habit_metrics(user_id, start_d, end_d)

    def get_goal_analytics(self, user_id: str) -> Dict[str, Any]:
        """Aggregate active goals and milestone progress."""
        return self.repo.get_goal_metrics(user_id)

    def get_financial_analytics(self, user_id: str, period: str = "month", **kwargs) -> Dict[str, Any]:
        """Aggregate income, expenses, and budget utilization."""
        start_utc, end_utc, start_d, _, _ = self.resolve_date_window(user_id, period, kwargs.get("start_date"), kwargs.get("end_date"), kwargs.get("timezone"))
        month_str = start_d.strftime("%Y-%m")
        return self.repo.get_financial_metrics(user_id, start_utc, end_utc, month_str)

    def get_trends_analytics(self, user_id: str, period: str = "week", **kwargs) -> Dict[str, Any]:
        """Aggregate daily activity trends across productivity and habits."""
        start_utc, end_utc, start_d, end_d, _ = self.resolve_date_window(
            user_id, period, kwargs.get("start_date"), kwargs.get("end_date"), kwargs.get("timezone")
        )
        task_data = self.repo.get_task_metrics(user_id, start_utc, end_utc)
        habit_data = self.repo.get_habit_metrics(user_id, start_d, end_d)

        task_trend = {item["date"]: item["completed"] for item in task_data.get("daily_completion_trend", [])}
        habit_trend = {item["date"]: item["completed"] for item in habit_data.get("daily_trend", [])}

        combined_trends = []
        curr = start_d
        while curr <= end_d:
            d_str = curr.isoformat()
            t_comp = task_trend.get(d_str, 0)
            h_comp = habit_trend.get(d_str, 0)
            combined_trends.append({
                "date": d_str,
                "tasks_completed": t_comp,
                "habits_completed": h_comp,
                "total_activity": t_comp + h_comp,
            })
            curr += timedelta(days=1)

        return {
            "period": period,
            "start_date": start_d.isoformat(),
            "end_date": end_d.isoformat(),
            "daily_trends": combined_trends,
        }

    # -------------------------------------------------------------------------
    # Life Score Engine
    # -------------------------------------------------------------------------

    def calculate_life_score(self, user_id: str, period: str = "week", **kwargs) -> Dict[str, Any]:
        """Compute transparent 4-pillar personal progress score with dynamic weight re-normalization."""
        prod = self.get_productivity_analytics(user_id, period, **kwargs)
        habits = self.get_habit_analytics(user_id, period, **kwargs)
        goals = self.get_goal_analytics(user_id)
        finance = self.get_financial_analytics(user_id, period, **kwargs)

        # Dimension 1: Productivity (Base Weight: 0.30)
        has_prod_data = (prod["total_tasks"] + prod["pending_tasks"] + prod["total_planner_blocks"]) > 0
        if has_prod_data:
            prod_score = round(
                (prod["completion_percentage"] * 0.7) + (prod["planner_completion_percentage"] * 0.3),
                1
            )
            prod_status = "excellent" if prod_score >= 80 else "good" if prod_score >= 60 else "needs_attention"
        else:
            prod_score = 100.0
            prod_status = "unpenalized_no_data"

        # Dimension 2: Habits (Base Weight: 0.30)
        has_habit_data = habits["total_active_habits"] > 0 and habits["total_scheduled_checkins"] > 0
        if has_habit_data:
            habit_score = habits["consistency_percentage"]
            habit_status = "excellent" if habit_score >= 80 else "good" if habit_score >= 60 else "needs_attention"
        else:
            habit_score = 100.0
            habit_status = "unpenalized_no_data"

        # Dimension 3: Goals (Base Weight: 0.20)
        has_goal_data = goals["total_goals"] > 0
        if has_goal_data:
            goal_score = round(
                (goals["completion_percentage"] * 0.5) + (goals["milestone_completion_percentage"] * 0.5),
                1
            )
            goal_status = "excellent" if goal_score >= 80 else "good" if goal_score >= 50 else "needs_attention"
        else:
            goal_score = 100.0
            goal_status = "unpenalized_no_data"

        # Dimension 4: Finance (Base Weight: 0.20)
        has_finance_data = float(finance["total_income"]) > 0 or float(finance["total_expenses"]) > 0 or len(finance["savings_goals_progress"]) > 0
        if has_finance_data:
            savings_component = min(100.0, finance["savings_rate"] * 2.0)  # 50% savings rate = 100 score
            adherence_component = finance["budget_adherence_percentage"]
            finance_score = round((savings_component * 0.5) + (adherence_component * 0.5), 1)
            finance_status = "excellent" if finance_score >= 80 else "good" if finance_score >= 60 else "needs_attention"
        else:
            finance_score = 100.0
            finance_status = "unpenalized_no_data"

        # Normalize weights if any pillar lacks data
        active_weights = {
            "productivity": 0.30 if has_prod_data else 0.0,
            "habits": 0.30 if has_habit_data else 0.0,
            "goals": 0.20 if has_goal_data else 0.0,
            "finance": 0.20 if has_finance_data else 0.0,
        }
        total_active_weight = sum(active_weights.values())

        if total_active_weight > 0:
            norm_weights = {k: v / total_active_weight for k, v in active_weights.items()}
        else:
            norm_weights = {"productivity": 0.25, "habits": 0.25, "goals": 0.25, "finance": 0.25}

        overall = round(
            (prod_score * norm_weights["productivity"]) +
            (habit_score * norm_weights["habits"]) +
            (goal_score * norm_weights["goals"]) +
            (finance_score * norm_weights["finance"])
        )
        overall = max(0, min(100, overall))

        if overall >= 85:
            tier = "Exceptional"
        elif overall >= 70:
            tier = "Strong"
        elif overall >= 50:
            tier = "Balanced"
        else:
            tier = "Building Momentum"

        dimensions = [
            {
                "name": "Productivity",
                "score": prod_score,
                "weight": round(norm_weights["productivity"] * 100, 1),
                "weighted_score": round(prod_score * norm_weights["productivity"], 1),
                "description": f"Tasks completion ({prod['completion_percentage']}%) and Planner adherence ({prod['planner_completion_percentage']}%).",
                "status": prod_status,
            },
            {
                "name": "Habits",
                "score": habit_score,
                "weight": round(norm_weights["habits"] * 100, 1),
                "weighted_score": round(habit_score * norm_weights["habits"], 1),
                "description": f"Habit consistency ({habits['consistency_percentage']}%) across {habits['total_active_habits']} active habits.",
                "status": habit_status,
            },
            {
                "name": "Goals",
                "score": goal_score,
                "weight": round(norm_weights["goals"] * 100, 1),
                "weighted_score": round(goal_score * norm_weights["goals"], 1),
                "description": f"Goal completion ({goals['completion_percentage']}%) and Milestones ({goals['milestone_completion_percentage']}%).",
                "status": goal_status,
            },
            {
                "name": "Financial Discipline",
                "score": finance_score,
                "weight": round(norm_weights["finance"] * 100, 1),
                "weighted_score": round(finance_score * norm_weights["finance"], 1),
                "description": f"Savings rate ({finance['savings_rate']}%) and Budget adherence ({finance['budget_adherence_percentage']}%).",
                "status": finance_status,
            },
        ]

        explanation = (
            f"Your Life Score of {overall}/100 represents a weighted composite of your verified personal habits, "
            f"task execution, milestone velocity, and budget adherence. Missing domains are normalized without penalty."
        )

        return {
            "overall_score": overall,
            "score_tier": tier,
            "period": period,
            "dimensions": dimensions,
            "calculation_explanation": explanation,
            "disclaimer": "This score is a personal productivity metric and is not a clinical, psychological, or medical assessment.",
        }

    # -------------------------------------------------------------------------
    # Comprehensive Overview
    # -------------------------------------------------------------------------

    def get_analytics_overview(self, user_id: str, period: str = "week", **kwargs) -> Dict[str, Any]:
        """Compile high-level multi-domain dashboard summary."""
        _, _, start_d, end_d, _ = self.resolve_date_window(user_id, period, kwargs.get("start_date"), kwargs.get("end_date"), kwargs.get("timezone"))
        life_score_data = self.calculate_life_score(user_id, period, **kwargs)
        prod = self.get_productivity_analytics(user_id, period, **kwargs)
        habits = self.get_habit_analytics(user_id, period, **kwargs)
        goals = self.get_goal_analytics(user_id)
        finance = self.get_financial_analytics(user_id, period, **kwargs)

        return {
            "period": period,
            "start_date": start_d.isoformat(),
            "end_date": end_d.isoformat(),
            "life_score": life_score_data["overall_score"],
            "life_score_tier": life_score_data["score_tier"],
            "productivity_summary": {
                "completed_tasks": prod["completed_tasks"],
                "total_tasks": prod["total_tasks"],
                "completion_percentage": prod["completion_percentage"],
                "completed_planner_blocks": prod["completed_planner_blocks"],
            },
            "habits_summary": {
                "active_habits": habits["total_active_habits"],
                "consistency_percentage": habits["consistency_percentage"],
                "best_streak": habits["best_streak_record"],
            },
            "goals_summary": {
                "active_goals": goals["active_goals"],
                "completed_goals": goals["completed_goals"],
                "completion_percentage": goals["completion_percentage"],
                "upcoming_deadlines_count": len(goals["upcoming_deadlines"]),
            },
            "finance_summary": {
                "total_income": finance["total_income"],
                "total_expenses": finance["total_expenses"],
                "net_savings": finance["net_savings"],
                "savings_rate": finance["savings_rate"],
            },
        }

    # -------------------------------------------------------------------------
    # AI Personal Insights Synthesis
    # -------------------------------------------------------------------------

    def generate_ai_insights(self, user_id: str, period: str = "week", **kwargs) -> Dict[str, Any]:
        """Synthesize narrative observations and actionable suggestions using local Qwen model."""
        overview = self.get_analytics_overview(user_id, period, **kwargs)
        score_data = self.calculate_life_score(user_id, period, **kwargs)

        # Fallback generator
        def build_fallback(is_fallback: bool = True) -> Dict[str, Any]:
            prod = overview["productivity_summary"]
            hab = overview["habits_summary"]
            fin = overview["finance_summary"]
            score = overview["life_score"]

            exec_summary = (
                f"You achieved an overall Life Score of {score}/100 for this {period}. "
                f"Your task completion reached {prod['completion_percentage']}% while habit consistency maintained {hab['consistency_percentage']}%."
            )
            prod_obs = (
                f"You completed {prod['completed_tasks']} tasks and executed {prod['completed_planner_blocks']} calendar blocks."
            )
            hab_obs = (
                f"Active streaks are steady across {hab['active_habits']} habits with a top record of {hab['best_streak']} consecutive days."
            )
            fin_obs = (
                f"Net savings totaled ${fin['net_savings']} yielding a {fin['savings_rate']}% savings rate."
            )
            recs = [
                "Protect morning focus blocks to maintain high task velocity.",
                "Do an evening check-in to preserve your daily habit streaks.",
                "Review category spending to maintain your targeted savings rate.",
            ]
            return {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period": period,
                "life_score": score,
                "executive_summary": exec_summary,
                "productivity_observation": prod_obs,
                "habit_observation": hab_obs,
                "financial_observation": fin_obs,
                "actionable_recommendations": recs,
                "is_fallback": is_fallback,
            }

        try:
            llm = get_llm(temperature=0.3)
            prompt = (
                f"You are LifeOS Analytics Engine. Analyze the user's verified metrics for the {period}:\n"
                f"- Life Score: {overview['life_score']}/100 ({overview['life_score_tier']})\n"
                f"- Productivity: {overview['productivity_summary']['completed_tasks']} tasks completed ({overview['productivity_summary']['completion_percentage']}%)\n"
                f"- Habits: {overview['habits_summary']['consistency_percentage']}% consistency across {overview['habits_summary']['active_habits']} habits\n"
                f"- Financials: ${overview['finance_summary']['net_savings']} net savings ({overview['finance_summary']['savings_rate']}% savings rate)\n\n"
                f"Return a strict JSON object with these exact keys:\n"
                f"- executive_summary: 1-2 sentence overall summary\n"
                f"- productivity_observation: 1 factual sentence on work patterns\n"
                f"- habit_observation: 1 factual sentence on consistency\n"
                f"- financial_observation: 1 factual sentence on spending & savings\n"
                f"- actionable_recommendations: list of 3 concise actionable tips\n"
                f"Do NOT invent unverified data."
            )
            messages = [
                SystemMessage(content="You are a personal productivity analyst. Return strict JSON only."),
                HumanMessage(content=prompt)
            ]
            response = llm.invoke(messages)
            text = response.content if hasattr(response, "content") else str(response)

            # Extract JSON block
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}") + 1]
                parsed = json.loads(json_str)
                return {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "period": period,
                    "life_score": overview["life_score"],
                    "executive_summary": parsed.get("executive_summary", ""),
                    "productivity_observation": parsed.get("productivity_observation", ""),
                    "habit_observation": parsed.get("habit_observation", ""),
                    "financial_observation": parsed.get("financial_observation", ""),
                    "actionable_recommendations": parsed.get("actionable_recommendations", []),
                    "is_fallback": False,
                }
            return build_fallback(is_fallback=True)
        except Exception:
            return build_fallback(is_fallback=True)
