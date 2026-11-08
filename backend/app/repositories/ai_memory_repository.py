"""LifeOS - AI Memory Repository.

Data access and persistence operations for AI memories (confirmed, pending, archived).
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy import or_, desc, asc
from app.extensions import db
from app.models.ai import AIMemory
from app.models.user_preference import UserPreference


class AIMemoryRepository:
    """Repository handling database operations for user AI memories."""

    def create_memory(
        self,
        user_id: str,
        memory_key: str,
        memory_value: str,
        memory_type: str = "fact",
        confidence: float = 1.0,
        status: str = "pending",
        source_conversation_id: Optional[str] = None,
        source_message_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> AIMemory:
        """Create and persist a new memory record."""
        memory = AIMemory(
            user_id=user_id,
            memory_key=memory_key.strip()[:100],
            memory_value=memory_value.strip(),
            memory_type=memory_type,
            confidence=confidence,
            status=status,
            source_conversation_id=source_conversation_id,
            source_message_id=source_message_id,
            expires_at=expires_at
        )
        db.session.add(memory)
        db.session.commit()
        return memory

    def get_by_id(self, memory_id: str) -> Optional[AIMemory]:
        """Retrieve memory by ID."""
        return AIMemory.query.filter_by(id=memory_id).first()

    def find_duplicate(
        self,
        user_id: str,
        memory_key: str,
        memory_type: str
    ) -> Optional[AIMemory]:
        """Check if an active or pending memory with similar key and type exists."""
        return (
            AIMemory.query
            .filter(
                AIMemory.user_id == user_id,
                AIMemory.memory_type == memory_type,
                AIMemory.memory_key.ilike(memory_key.strip()),
                AIMemory.status.in_(["confirmed", "pending"])
            )
            .first()
        )

    def list_for_user(
        self,
        user_id: str,
        status: str = "confirmed",
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[AIMemory], int]:
        """List user memories filtered by status, category, and search text."""
        query = AIMemory.query.filter(
            AIMemory.user_id == user_id,
            AIMemory.status == status
        )

        if category:
            query = query.filter(AIMemory.memory_type == category)

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    AIMemory.memory_key.ilike(search_pattern),
                    AIMemory.memory_value.ilike(search_pattern)
                )
            )

        total = query.count()
        items = (
            query
            .order_by(desc(AIMemory.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def update_memory(
        self,
        memory: AIMemory,
        updates: Dict[str, Any]
    ) -> AIMemory:
        """Update allowed fields of a memory."""
        for k, v in updates.items():
            if hasattr(memory, k):
                setattr(memory, k, v)
        db.session.commit()
        return memory

    def delete_memory(self, memory: AIMemory) -> None:
        """Permanently delete a memory record."""
        db.session.delete(memory)
        db.session.commit()

    def get_user_memory_preference(self, user_id: str) -> bool:
        """Check if personalization is enabled for the user."""
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if pref:
            return pref.ai_memory_enabled
        return True

    def set_user_memory_preference(self, user_id: str, enabled: bool) -> bool:
        """Toggle AI memory personalization on or off."""
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id, ai_memory_enabled=enabled)
            db.session.add(pref)
        else:
            pref.ai_memory_enabled = enabled
        db.session.commit()
        return pref.ai_memory_enabled

