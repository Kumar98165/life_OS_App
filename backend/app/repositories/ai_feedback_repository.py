"""LifeOS - AI Feedback Repository Layer.

Data access and persistence for assistant interaction feedback, ratings,
and user corrections.
"""
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import desc
from app.extensions import db
from app.models.ai import AIFeedback
class AIFeedbackRepository:
    """Repository handling CRUD and queries for AIFeedback records."""
    def create_or_update(
        self,
        user_id: str,
        message_id: str,
        rating: int,
        feedback_type: str,
        category: Optional[str] = None,
        comment: Optional[str] = None,
        suggested_response: Optional[str] = None
    ) -> Tuple[AIFeedback, bool]:
        """Create a new feedback record or update existing one for the message.

        Enforces strictly one feedback record per assistant message without duplicate rows.
        Returns:
            Tuple[AIFeedback, bool]: (feedback_instance, was_created)
        """
        existing = self.get_by_message_id(message_id)
        if existing:
            existing.rating = rating
            existing.feedback_type = feedback_type
            existing.category = category
            existing.comment = comment
            existing.suggested_response = suggested_response
            existing.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return existing, False

        feedback = AIFeedback(
            user_id=user_id,
            message_id=message_id,
            rating=rating,
            feedback_type=feedback_type,
            category=category,
            comment=comment,
            suggested_response=suggested_response
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback, True

    def get_by_id(self, feedback_id: str) -> Optional[AIFeedback]:
        """Retrieve feedback by primary key ID."""
        return db.session.get(AIFeedback, feedback_id)

    def get_by_message_id(self, message_id: str) -> Optional[AIFeedback]:
        """Retrieve feedback associated with a specific message ID."""
        return AIFeedback.query.filter_by(message_id=message_id).first()

    def update(self, feedback: AIFeedback, updates: Dict[str, Any]) -> AIFeedback:
        """Update mutable fields of an existing feedback record."""
        allowed_fields = {"rating", "feedback_type", "category", "comment", "suggested_response"}
        for k, v in updates.items():
            if k in allowed_fields:
                setattr(feedback, k, v)
        feedback.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return feedback

    def delete(self, feedback: AIFeedback) -> None:
        """Permanently delete a feedback record."""
        db.session.delete(feedback)
        db.session.commit()

    def list_for_user(
        self,
        user_id: str,
        rating: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[AIFeedback], int]:
        """List feedback records for authenticated user with pagination and optional rating filter."""
        query = AIFeedback.query.filter_by(user_id=user_id)
        if rating is not None:
            query = query.filter(AIFeedback.rating == rating)

        total = query.count()
        items = (
            query
            .order_by(desc(AIFeedback.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total
