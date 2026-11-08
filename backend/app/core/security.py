from typing import Optional
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.models.auth_token import RefreshToken
from app.models.user import User
from app.extensions import jwt, db


def check_resource_ownership(resource_user_id: Optional[str], current_user_id: Optional[str]) -> None:
    """Enforce strict user-level resource authorization boundaries."""
    if not current_user_id:
        raise UnauthorizedException("Authentication identity required")
    if not resource_user_id or str(resource_user_id) != str(current_user_id):
        raise ForbiddenException("You do not have permission to access or modify this resource")


def admin_required():
    """Decorator to enforce that the authenticated user possesses the 'admin' role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if not user_id:
                raise UnauthorizedException("Authentication identity required")
            user = db.session.get(User, user_id)
            if not user or user.role != "admin":
                raise ForbiddenException("Administrator privileges required for this action")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
def init_token_blocklist(jwt_manager) -> None:
    """Configure JWT blocklist verification against database refresh tokens."""

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        """Check if JWT refresh token is revoked."""
        token_type = jwt_payload.get("type")
        if token_type != "refresh":
            return False  # Short-lived access tokens do not hit DB on every request

        jti = jwt_payload.get("jti")
        if not jti:
            return False

        token = RefreshToken.query.filter_by(token_jti=jti).first()
        if token is None:
            # If a refresh token is not found in persistent store, consider revoked
            return False
        return token.is_revoked

