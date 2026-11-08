from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import limiter
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth_service import AuthService
from app.core.response import api_response

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """Register a new user account."""
    json_data = request.get_json(silent=True) or {}
    validated = RegisterRequest(**json_data)

    user, tokens = auth_service.register_user(
        email=validated.email,
        plain_password=validated.password,
        full_name=validated.full_name
    )

    return api_response(
        data={
            "user": user.to_dict(),
            "tokens": tokens
        },
        message="User account created successfully",
        status_code=201
    )


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("15 per minute")
def login():
    """Authenticate user with email and password."""
    json_data = request.get_json(silent=True) or {}
    validated = LoginRequest(**json_data)

    user, tokens = auth_service.authenticate_user(
        email=validated.email,
        plain_password=validated.password
    )

    return api_response(
        data={
            "user": user.to_dict(),
            "tokens": tokens
        },
        message="Authentication successful",
        status_code=200
    )
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """Rotate refresh token and issue new access & refresh token pair."""
    user_id = get_jwt_identity()
    current_jti = get_jwt().get("jti")
    rotated_tokens = auth_service.rotate_refresh_token(user_id, current_jti)

    return api_response(
        data=rotated_tokens,
        message="Token pair rotated successfully"
    )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():
    """Revoke current refresh token to terminate session."""
    jwt_payload = get_jwt()
    jti = jwt_payload.get("jti")
    if jti:
        auth_service.revoke_refresh_token(jti)

    return api_response(
        data={},
        message="Logged out successfully; refresh token revoked"
    )
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """Get profile of current authenticated user."""
    user_id = get_jwt_identity()
    user = auth_service.get_current_user(user_id)

    return api_response(
        data={"user": user.to_dict()},
        message="Profile retrieved successfully"
    )
