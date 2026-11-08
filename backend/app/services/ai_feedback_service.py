"""LifeOS - AI Feedback Service Layer.

Handles business logic for assistant feedback submissions, ratings,
corrections, privacy consent management, and IDOR boundary enforcement.
"""
from typing import Optional, Dict, Any, Tuple
from app.extensions import db
from app.models.ai import AIMessage, AIConversation, AIFeedback, AITrainingSample
from app.models.user_preference import UserPreference
from app.repositories.ai_feedback_repository import AIFeedbackRepository
from app.schemas.ai_feedback import (
    SUPPORTED_FEEDBACK_CATEGORIES,
    SUPPORTED_FEEDBACK_TYPES,
)
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.core.security import check_resource_ownership


class AIFeedbackService:
    """Service orchestrating AI response feedback collection and training privacy."""

    def __init__(self, feedback_repo: Optional[AIFeedbackRepository] = None):
        self.feedback_repo = feedback_repo or AIFeedbackRepository()

    def submit_feedback(
        self,
        user_id: str,
        message_id: str,
        rating: int,
        feedback_type: Optional[str] = None,
        category: Optional[str] = None,
        comment: Optional[str] = None,
        suggested_response: Optional[str] = None
    ) -> Tuple[AIFeedback, bool]:
        """Submit feedback for an assistant message.

        Validates message existence, ensures message belongs to authenticated user's conversation,
        verifies message role is 'assistant', and handles idempotent creation/update.

        Returns:
            Tuple[AIFeedback, bool]: (feedback, is_created)
        """
        if rating not in (1, -1):
            raise BadRequestException("Rating must be +1 (thumbs up) or -1 (thumbs down)")

        if category and category not in SUPPORTED_FEEDBACK_CATEGORIES:
            raise BadRequestException(
                f"Invalid category '{category}'. Must be one of {SUPPORTED_FEEDBACK_CATEGORIES}"
            )

        if feedback_type and feedback_type not in SUPPORTED_FEEDBACK_TYPES:
            raise BadRequestException(
                f"Invalid feedback_type '{feedback_type}'. Must be one of {SUPPORTED_FEEDBACK_TYPES}"
            )

        # 1. Fetch referenced message
        message = db.session.get(AIMessage, message_id)
        if not message:
            raise NotFoundException("Assistant message not found")

        # 2. Verify conversation ownership (Anti-IDOR)
        conversation = db.session.get(AIConversation, message.conversation_id)
        if not conversation or str(conversation.user_id) != str(user_id):
            raise ForbiddenException("You do not have permission to access or modify this resource")

        # 3. Only assistant messages can receive feedback
        if message.role != "assistant":
            raise BadRequestException("Feedback can only be submitted for assistant messages")

        # 4. Resolve default feedback_type if unspecified
        resolved_type = feedback_type
        if not resolved_type:
            if suggested_response:
                resolved_type = "correction"
            elif rating == 1:
                resolved_type = "thumbs_up"
            else:
                resolved_type = "thumbs_down"

        # 5. Persist or update feedback record
        feedback, was_created = self.feedback_repo.create_or_update(
            user_id=user_id,
            message_id=message_id,
            rating=rating,
            feedback_type=resolved_type,
            category=category,
            comment=comment,
            suggested_response=suggested_response
        )

        return feedback, was_created

    def get_feedback_by_id(self, feedback_id: str, current_user_id: str) -> AIFeedback:
        """Retrieve feedback by ID ensuring authenticated user ownership."""
        feedback = self.feedback_repo.get_by_id(feedback_id)
        if not feedback:
            raise NotFoundException("Feedback not found")
        check_resource_ownership(feedback.user_id, current_user_id)
        return feedback

    def get_feedback_for_message(self, message_id: str, current_user_id: str) -> AIFeedback:
        """Retrieve feedback for a specific assistant message ensuring conversation ownership."""
        message = db.session.get(AIMessage, message_id)
        if not message:
            raise NotFoundException("Assistant message not found")

        conversation = db.session.get(AIConversation, message.conversation_id)
        if not conversation or str(conversation.user_id) != str(current_user_id):
            raise ForbiddenException("You do not have permission to access or modify this resource")

        feedback = self.feedback_repo.get_by_message_id(message_id)
        if not feedback:
            raise NotFoundException("No feedback found for this message")

        return feedback

    def update_feedback(
        self,
        feedback_id: str,
        current_user_id: str,
        updates: Dict[str, Any]
    ) -> AIFeedback:
        """Update mutable fields of a feedback record ensuring ownership."""
        feedback = self.get_feedback_by_id(feedback_id, current_user_id)

        if "rating" in updates and updates["rating"] is not None:
            if updates["rating"] not in (1, -1):
                raise BadRequestException("Rating must be +1 (thumbs up) or -1 (thumbs down)")

        if "category" in updates and updates["category"] is not None:
            if updates["category"] not in SUPPORTED_FEEDBACK_CATEGORIES:
                raise BadRequestException(
                    f"Invalid category '{updates['category']}'. Must be one of {SUPPORTED_FEEDBACK_CATEGORIES}"
                )

        if "feedback_type" in updates and updates["feedback_type"] is not None:
            if updates["feedback_type"] not in SUPPORTED_FEEDBACK_TYPES:
                raise BadRequestException(
                    f"Invalid feedback_type '{updates['feedback_type']}'. Must be one of {SUPPORTED_FEEDBACK_TYPES}"
                )

        return self.feedback_repo.update(feedback, updates)

    def delete_feedback(self, feedback_id: str, current_user_id: str) -> None:
        """Permanently delete a feedback record ensuring ownership."""
        feedback = self.get_feedback_by_id(feedback_id, current_user_id)
        self.feedback_repo.delete(feedback)

    def list_feedback(
        self,
        user_id: str,
        rating: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List feedback submissions for authenticated user with pagination."""
        items, total = self.feedback_repo.list_for_user(
            user_id=user_id,
            rating=rating,
            limit=limit,
            offset=offset
        )
        return {
            "feedback": [f.to_dict() for f in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    # ---------------------------------------------------------
    # Training Privacy & Consent Management
    # ---------------------------------------------------------

    def get_training_consent(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user's current AI training data contribution consent status."""
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id, ai_training_consent=False)
            db.session.add(pref)
            db.session.commit()

        return {
            "user_id": user_id,
            "ai_training_consent": pref.ai_training_consent,
            "policy_version": "v1.0",
            "privacy_notice": (
                "When enabled, your feedback and anonymized corrections may be used "
                "to fine-tune local LifeOS models. Consent defaults to false, is completely "
                "optional, and can be withdrawn at any time."
            )
        }

    def update_training_consent(self, user_id: str, consent: bool) -> Dict[str, Any]:
        """Update AI training consent preference.

        When consent is withdrawn (consent=False):
        Transactionally updates the preference and revokes consent on all existing
        training samples associated with this user (setting consent_status='revoked').
        Existing user feedback records remain preserved.
        """
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id, ai_training_consent=consent)
            db.session.add(pref)
        else:
            pref.ai_training_consent = consent

        samples_revoked = 0
        if not consent:
            # Transactionally invalidate training samples for this user
            samples_revoked = AITrainingSample.query.filter_by(user_id=user_id).update(
                {"consent_status": "revoked"}
            )

        db.session.commit()

        return {
            "user_id": user_id,
            "ai_training_consent": pref.ai_training_consent,
            "samples_revoked": samples_revoked,
            "message": "AI training consent preference updated successfully"
        }
