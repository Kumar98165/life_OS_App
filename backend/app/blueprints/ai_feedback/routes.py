"""LifeOS - AI Feedback & Training Privacy Blueprint Routes.

Endpoints for assistant response rating, feedback collection, corrections,
and user training data privacy consent.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.ai_feedback import (
    SubmitFeedbackRequest,
    UpdateFeedbackRequest,
    UpdateConsentRequest,
)
from app.services.ai_feedback_service import AIFeedbackService
from app.core.response import api_response

ai_feedback_bp = Blueprint("ai_feedback", __name__)
feedback_service = AIFeedbackService()


# ---------------------------------------------------------
# Feedback CRUD & Message Query
# ---------------------------------------------------------

@ai_feedback_bp.route("/feedback", methods=["POST"])
@jwt_required()
def submit_feedback():
    """Submit rating and optional feedback for an assistant turn.

    If feedback for the specified message already exists, updates the record
    without creating a duplicate row.
    """
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = SubmitFeedbackRequest(**json_data)

    feedback, was_created = feedback_service.submit_feedback(
        user_id=user_id,
        message_id=validated.message_id,
        rating=validated.rating,
        feedback_type=validated.feedback_type,
        category=validated.category,
        comment=validated.comment,
        suggested_response=validated.suggested_response
    )

    status_code = 201 if was_created else 200
    msg = "Feedback submitted successfully" if was_created else "Feedback updated successfully"
    return api_response(
        data={"feedback": feedback.to_dict()},
        message=msg,
        status_code=status_code
    )


@ai_feedback_bp.route("/feedback", methods=["GET"])
@jwt_required()
def list_feedback():
    """List feedback submissions belonging to the authenticated user."""
    user_id = get_jwt_identity()
    rating = request.args.get("rating", type=int)
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    result = feedback_service.list_feedback(
        user_id=user_id,
        rating=rating,
        limit=min(max(limit, 1), 100),
        offset=max(offset, 0)
    )

    return api_response(
        data=result,
        message="Feedback list retrieved successfully"
    )


@ai_feedback_bp.route("/feedback/<feedback_id>", methods=["GET"])
@jwt_required()
def get_feedback(feedback_id: str):
    """Retrieve a specific feedback record by ID."""
    user_id = get_jwt_identity()
    feedback = feedback_service.get_feedback_by_id(feedback_id=feedback_id, current_user_id=user_id)

    return api_response(
        data={"feedback": feedback.to_dict()},
        message="Feedback retrieved successfully"
    )


@ai_feedback_bp.route("/feedback/<feedback_id>", methods=["PATCH"])
@jwt_required()
def update_feedback(feedback_id: str):
    """Update fields of an existing feedback record."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateFeedbackRequest(**json_data)

    updates = validated.model_dump(exclude_unset=True)
    updated = feedback_service.update_feedback(
        feedback_id=feedback_id,
        current_user_id=user_id,
        updates=updates
    )

    return api_response(
        data={"feedback": updated.to_dict()},
        message="Feedback updated successfully"
    )


@ai_feedback_bp.route("/feedback/<feedback_id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id: str):
    """Permanently delete a feedback record."""
    user_id = get_jwt_identity()
    feedback_service.delete_feedback(feedback_id=feedback_id, current_user_id=user_id)

    return api_response(
        data=None,
        message="Feedback deleted successfully"
    )


@ai_feedback_bp.route("/messages/<message_id>/feedback", methods=["GET"])
@jwt_required()
def get_message_feedback(message_id: str):
    """Retrieve feedback attached to a specific assistant message."""
    user_id = get_jwt_identity()
    feedback = feedback_service.get_feedback_for_message(message_id=message_id, current_user_id=user_id)

    return api_response(
        data={"feedback": feedback.to_dict()},
        message="Message feedback retrieved successfully"
    )


# ---------------------------------------------------------
# Training Privacy & Consent API
# ---------------------------------------------------------

@ai_feedback_bp.route("/learning/consent", methods=["GET"])
@jwt_required()
def get_training_consent():
    """Retrieve current AI training consent preferences."""
    user_id = get_jwt_identity()
    consent_info = feedback_service.get_training_consent(user_id=user_id)

    return api_response(
        data=consent_info,
        message="AI training consent preferences retrieved successfully"
    )


@ai_feedback_bp.route("/learning/consent", methods=["PATCH"])
@jwt_required()
def update_training_consent():
    """Update AI training consent preference.

    When consent is withdrawn, automatically and transactionally invalidates
    existing candidate training samples by setting their status to 'revoked'.
    """
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateConsentRequest(**json_data)

    result = feedback_service.update_training_consent(
        user_id=user_id,
        consent=validated.ai_training_consent
    )

    return api_response(
        data=result,
        message=result["message"]
    )

