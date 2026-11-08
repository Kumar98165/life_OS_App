import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.models.user import User
from app.core.exceptions import ConflictException, UnauthorizedException, NotFoundException

logger = logging.getLogger(__name__)


class AuthService:
    """Core authentication, session lifecycle, and token rotation business service."""

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        token_repo: Optional[TokenRepository] = None
    ):
        self.user_repo = user_repo or UserRepository()
        self.token_repo = token_repo or TokenRepository()

    def register_user(self, email: str, plain_password: str, full_name: str) -> Tuple[User, Dict[str, str]]:
        """Register a new user account with normalized email, returning entity and tokens."""
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException(f"An account with email '{email}' already exists")

        user = self.user_repo.create(
            email=email,
            plain_password=plain_password,
            full_name=full_name
        )

        tokens = self.generate_tokens(user.id)
        return user, tokens

    def authenticate_user(self, email: str, plain_password: str) -> Tuple[User, Dict[str, str]]:
        """Verify user credentials and generate tokens. Uses constant-time response messaging."""
        user = self.user_repo.get_by_email(email)
        # Verify credentials safely to prevent account enumeration
        if not user or not user.check_password(plain_password):
            raise UnauthorizedException("Invalid email or password credentials")

        if not user.is_active:
            raise UnauthorizedException("User account is deactivated")

        tokens = self.generate_tokens(user.id)
        return user, tokens

    def get_current_user(self, user_id: str) -> User:
        """Fetch current authenticated user profile."""
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise NotFoundException("User account not found or deactivated")
        return user

    def update_user_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Update permitted profile attributes for authenticated user."""
        user = self.get_current_user(user_id)
        return self.user_repo.update_profile(user, full_name=full_name, avatar_url=avatar_url)

    def rotate_refresh_token(self, user_id: str, current_jti: str) -> Dict[str, str]:
        """
        Execute Refresh Token Rotation.
        Revokes previous JTI and issues a new access and refresh token pair.
        Detects token reuse: if current_jti is already revoked, terminates all active sessions.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User account is invalid or deactivated")

        # Check existing token in database
        token_record = self.token_repo.get_by_jti(current_jti)
        if token_record and token_record.is_revoked:
            # Token reuse attack detected! Revoke all tokens for user
            logger.warning(
                f"Token reuse detected for user_id={user_id} with jti={current_jti}. "
                "Revoking all active refresh tokens."
            )
            self.token_repo.revoke_all_for_user(user_id)
            raise UnauthorizedException("Revoked token reuse detected. All active sessions have been terminated.")

        # Revoke the current refresh token
        self.token_repo.revoke_by_jti(current_jti)

        # Issue new token pair
        return self.generate_tokens(user.id)

    def revoke_refresh_token(self, jti: str) -> bool:
        """Revoke a refresh token by JTI upon user logout."""
        return self.token_repo.revoke_by_jti(jti)

    def generate_tokens(self, user_id: str) -> Dict[str, str]:
        """Generate JWT access and refresh token pair and persist refresh token JTI."""
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        try:
            decoded = decode_token(refresh_token)
            jti = decoded.get("jti")
            exp_timestamp = decoded.get("exp")
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) if exp_timestamp else None

            if jti and expires_at:
                self.token_repo.create(
                    user_id=user_id,
                    token_jti=jti,
                    expires_at=expires_at
                )
        except Exception as e:
            logger.error(f"Failed to persist refresh token JTI: {str(e)}", exc_info=True)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
