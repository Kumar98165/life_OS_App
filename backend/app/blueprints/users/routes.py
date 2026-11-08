from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.user import UpdateProfileRequest
from app.services.auth_service import AuthService
from app.core.response import api_response

users_bp = Blueprint("users", __name__)
auth_service = AuthService()


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user_profile():
    """Retrieve profile of currently authenticated user."""
    user_id = get_jwt_identity()
    user = auth_service.get_current_user(user_id)

    return api_response(
        data={"user": user.to_dict()},
        message="Profile retrieved successfully"
    )


@users_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_profile():
    """Update profile fields (full_name, avatar_url) for currently authenticated user."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateProfileRequest(**json_data)

    updated_user = auth_service.update_user_profile(
        user_id=user_id,
        full_name=validated.full_name,
        avatar_url=validated.avatar_url
    )

    return api_response(
        data={"user": updated_user.to_dict()},
        message="Profile updated successfully"
    )

