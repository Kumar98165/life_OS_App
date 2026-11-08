from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator

class DateRangeParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: Optional[str] = Field("week", pattern="^(day|week|month|year|custom)$")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    timezone: Optional[str] = "UTC"

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Dates must be formatted as YYYY-MM-DD")
        return v
class ProductivityAnalytics(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    completion_percentage: float
    total_planner_blocks: int
    completed_planner_blocks: int
    planner_completion_percentage: float
    daily_completion_trend: List[Dict[str, Any]]
    planner_distribution: List[Dict[str, Any]]
class HabitAnalytics(BaseModel):
    total_active_habits: int
    total_scheduled_checkins: int
    total_completed_checkins: int
    consistency_percentage: float
    average_current_streak: float
    best_streak_record: int
    habits_performance: List[Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]


class GoalAnalytics(BaseModel):
    total_goals: int
    active_goals: int
    completed_goals: int
    completion_percentage: float
    total_milestones: int
    completed_milestones: int
    milestone_completion_percentage: float
    goals_progress: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]
class FinancialAnalytics(BaseModel):
    period: str
    total_income: str
    total_expenses: str
    net_savings: str
    savings_rate: float
    spending_by_category: List[Dict[str, Any]]
    budget_adherence_percentage: float
    savings_goals_progress: List[Dict[str, Any]]


class LifeScoreDimension(BaseModel):
    name: str
    score: float
    weight: float
    weighted_score: float
    description: str
    status: str  # excellent, good, fair, needs_attention, unpenalized_no_data


class LifeScoreResponse(BaseModel):
    overall_score: int
    score_tier: str  # Exceptional, Strong, Balanced, Building Momentum
    period: str
    dimensions: List[LifeScoreDimension]
    calculation_explanation: str
    disclaimer: str


class AnalyticsOverviewResponse(BaseModel):
    period: str
    start_date: str
    end_date: str
    life_score: int
    life_score_tier: str
    productivity_summary: Dict[str, Any]
    habits_summary: Dict[str, Any]
    goals_summary: Dict[str, Any]
    finance_summary: Dict[str, Any]
class AIInsightsResponse(BaseModel):
    generated_at: str
    period: str
    life_score: int
    executive_summary: str
    productivity_observation: str
    habit_observation: str
    financial_observation: str
    actionable_recommendations: List[str]
    is_fallback: bool
