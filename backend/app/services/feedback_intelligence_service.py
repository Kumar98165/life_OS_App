"""LifeOS - Feedback Intelligence & Analytics Engine.

Provides deterministic user-scoped analytics, negative feedback clustering,
appreciation quality aggregation, trends analysis, and actionable AI improvement recommendations.
Enforces multi-user isolation, zero external cloud exposure, and strict read-only safety.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, desc
from app.extensions import db
from app.models.ai import AIFeedback, AIMessage


class FeedbackIntelligenceService:
    """Business logic for feedback pattern extraction, analytics, and recommendation synthesis."""

    def get_user_feedback_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Compute user-scoped statistics on assistant responses for the specified time window."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Base query scoped strictly to user
        query = AIFeedback.query.filter(
            AIFeedback.user_id == user_id,
            AIFeedback.created_at >= cutoff
        )

        total_count = query.count()
        positive_count = query.filter(AIFeedback.rating == 1).count()
        negative_count = query.filter(AIFeedback.rating == -1).count()

        satisfaction_percentage = round((positive_count / total_count * 100.0), 1) if total_count > 0 else None

        # Frequency of negative feedback categories
        category_rows = (
            db.session.query(AIFeedback.category, func.count(AIFeedback.id))
            .filter(
                AIFeedback.user_id == user_id,
                AIFeedback.rating == -1,
                AIFeedback.category.isnot(None),
                AIFeedback.created_at >= cutoff
            )
            .group_by(AIFeedback.category)
            .order_by(desc(func.count(AIFeedback.id)))
            .all()
        )
        negative_categories_breakdown = {cat: count for cat, count in category_rows}

        # Feedback types breakdown
        type_rows = (
            db.session.query(AIFeedback.feedback_type, func.count(AIFeedback.id))
            .filter(AIFeedback.user_id == user_id, AIFeedback.created_at >= cutoff)
            .group_by(AIFeedback.feedback_type)
            .all()
        )
        feedback_types_breakdown = {ft: count for ft, count in type_rows}

        # Generate targeted improvement recommendations
        recommendations = self.generate_improvement_recommendations(negative_categories_breakdown, total_count, positive_count)

        return {
            "user_id": user_id,
            "window_days": days,
            "total_feedback_count": total_count,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "satisfaction_percentage": satisfaction_percentage,
            "negative_categories": negative_categories_breakdown,
            "feedback_types": feedback_types_breakdown,
            "improvement_recommendations": recommendations,
        }

    def generate_improvement_recommendations(
        self,
        negative_categories: Dict[str, int],
        total_feedback: int,
        positive_feedback: int
    ) -> List[Dict[str, Any]]:
        """Synthesize actionable, traceable improvement recommendations from feedback distribution."""
        recommendations = []

        if not negative_categories and total_feedback == 0:
            return [{
                "area": "general",
                "recommendation": "No feedback collected yet. Rate responses with thumbs up/down to personalize recommendations.",
                "severity": "info"
            }]

        if negative_categories.get("poor_explanation", 0) >= 1 or negative_categories.get("incomplete_answer", 0) >= 1:
            recommendations.append({
                "area": "clarity_and_completeness",
                "recommendation": "Structure responses with step-by-step numbered breakdowns and ensure comprehensive task coverage.",
                "severity": "high" if negative_categories.get("incomplete_answer", 0) > 2 else "medium"
            })

        if negative_categories.get("incorrect_answer", 0) >= 1:
            recommendations.append({
                "area": "factual_consistency",
                "recommendation": "Prioritize strict grounding in verified LifeOS database context over creative extrapolation.",
                "severity": "high"
            })

        if negative_categories.get("wrong_tone", 0) >= 1:
            recommendations.append({
                "area": "tone_and_style",
                "recommendation": "Align communication style with user's selected personalization tone (concise vs detailed).",
                "severity": "medium"
            })

        if negative_categories.get("outdated_context", 0) >= 1:
            recommendations.append({
                "area": "temporal_freshness",
                "recommendation": "Refresh today's planner blocks and purge unconfirmed or expired memories.",
                "severity": "medium"
            })

        if negative_categories.get("irrelevant_answer", 0) >= 1:
            recommendations.append({
                "area": "relevance",
                "recommendation": "Focus strictly on the user's specific query without extraneous domain summaries.",
                "severity": "medium"
            })

        if not recommendations and positive_feedback > 0:
            recommendations.append({
                "area": "high_satisfaction",
                "recommendation": "Response patterns are performing well. Current prompt configuration and memory retrieval meet user preferences.",
                "severity": "positive"
            })

        return recommendations


feedback_intelligence_service = FeedbackIntelligenceService()
