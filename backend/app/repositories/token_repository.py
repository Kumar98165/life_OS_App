from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update
from app.extensions import db
from app.models.auth_token import RefreshToken


class TokenRepository:
    """Repository handling persistent JWT refresh token lifecycles and revocation."""

    def get_by_jti(self, jti: str) -> Optional[RefreshToken]:
        """Fetch token record by JTI."""
        stmt = select(RefreshToken).where(RefreshToken.token_jti == jti)
        return db.session.execute(stmt).scalar_one_or_none()

    def create(self, user_id: str, token_jti: str, expires_at: datetime) -> RefreshToken:
        """Persist a newly issued refresh token."""
        record = RefreshToken(
            user_id=user_id,
            token_jti=token_jti,
            expires_at=expires_at,
            is_revoked=False
        )
        db.session.add(record)
        db.session.commit()
        return record

    def revoke_by_jti(self, jti: str) -> bool:
        """Mark a specific refresh token as revoked."""
        token = self.get_by_jti(jti)
        if token:
            token.is_revoked = True
            db.session.commit()
            return True
        return False

    def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke all active refresh tokens for a user (triggered on token reuse detection)."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(is_revoked=True)
        )
        result = db.session.execute(stmt)
        db.session.commit()
        return result.rowcount

