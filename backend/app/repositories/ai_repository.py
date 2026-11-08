"""LifeOS - AI Conversation Repository.

Handles database persistence for AI chat threads and discrete dialogue messages.
"""
from typing import Optional, List
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.ai import AIConversation, AIMessage


class AIConversationRepository:
    """Repository handling database operations for AI conversations and messages."""

    def create_conversation(
        self,
        user_id: str,
        title: str = "New Conversation",
        model_used: str = "qwen2.5:3b"
    ) -> AIConversation:
        """Create and persist a new chat thread."""
        conv = AIConversation(
            user_id=user_id,
            title=title,
            model_used=model_used
        )
        db.session.add(conv)
        db.session.commit()
        return conv

    def get_by_id(self, conversation_id: str) -> Optional[AIConversation]:
        """Retrieve conversation with eager-loaded messages."""
        return (
            AIConversation.query
            .options(selectinload(AIConversation.messages))
            .filter_by(id=conversation_id)
            .first()
        )

    def list_for_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[AIConversation]:
        """List chat threads belonging to user ordered by last update."""
        return (
            AIConversation.query
            .options(selectinload(AIConversation.messages))
            .filter_by(user_id=user_id)
            .order_by(AIConversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_title(self, conversation: AIConversation, new_title: str) -> AIConversation:
        """Update the display title of a chat thread."""
        conversation.title = new_title[:255]
        db.session.commit()
        return conversation

    def delete_conversation(self, conversation: AIConversation) -> None:
        """Permanently delete conversation and cascade-delete its messages."""
        db.session.delete(conversation)
        db.session.commit()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tokens_used: Optional[int] = None,
        prompt_version_id: Optional[str] = None,
        latency_ms: Optional[int] = None
    ) -> AIMessage:
        """Persist a message turn in a conversation."""
        msg = AIMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tokens_used=tokens_used,
            prompt_version_id=prompt_version_id,
            latency_ms=latency_ms
        )
        db.session.add(msg)
        db.session.commit()
        return msg

    def get_messages(self, conversation_id: str, limit: int = 20) -> List[AIMessage]:
        """Retrieve latest messages for a conversation in chronological order."""
        # Query latest `limit` messages, then order ascending
        subq = (
            AIMessage.query
            .filter_by(conversation_id=conversation_id)
            .order_by(AIMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(subq))

