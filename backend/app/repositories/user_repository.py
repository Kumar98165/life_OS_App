from typing import Optional
from sqlalchemy import select
from app.extensions import db
from app.models.user import User


class UserRepository:
    """Data access repository for User entities."""

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Fetch user by primary key ID."""
        return db.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by unique normalized email."""
        stmt = select(User).where(User.email == email.strip().lower())
        return db.session.execute(stmt).scalar_one_or_none()

    def create(self, email: str, plain_password: str, full_name: str) -> User:
        """Create and persist a new user entity."""
        user = User(
            email=email.strip().lower(),
            full_name=full_name.strip()
        )
        user.set_password(plain_password)
        db.session.add(user)
        db.session.commit()
        return user

    def update_profile(
        self,
        user: User,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Update permitted profile fields on an existing user."""
        if full_name is not None:
            user.full_name = full_name.strip()
        if avatar_url is not None:
            user.avatar_url = avatar_url.strip() if avatar_url else None
        db.session.commit()
        return user

    def update(self, user: User) -> User:
        """Persist changes to an existing user."""
        db.session.commit()
        return user
