"""LifeOS - AI Memory Service Layer.

Coordinates memory extraction, candidate suggestions, user approval workflows,
deterministic retrieval, and privacy settings.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from app.repositories.ai_memory_repository import AIMemoryRepository
from app.ai.memory.extractor import MemoryExtractionEngine, VALID_MEMORY_CATEGORIES
from app.ai.memory.retriever import MemoryRetrievalEngine
from app.models.ai import AIMemory
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.security import check_resource_ownership


class AIMemoryService:
    """Service orchestrating user memory approval, extraction, and retrieval."""

    def __init__(
        self,
        memory_repo: Optional[AIMemoryRepository] = None,
        extractor: Optional[MemoryExtractionEngine] = None,
        retriever: Optional[MemoryRetrievalEngine] = None
    ):
        self.memory_repo = memory_repo or AIMemoryRepository()
        self.extractor = extractor or MemoryExtractionEngine()
        self.retriever = retriever or MemoryRetrievalEngine()

    def list_confirmed_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List active confirmed memories for the user."""
        items, total = self.memory_repo.list_for_user(
            user_id=user_id,
            status="confirmed",
            category=category,
            search=search,
            limit=limit,
            offset=offset
        )
        return {
            "memories": [m.to_dict() for m in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def list_pending_suggestions(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List unapproved candidate memories waiting for user review."""
        items, total = self.memory_repo.list_for_user(
            user_id=user_id,
            status="pending",
            limit=limit,
            offset=offset
        )
        return {
            "suggestions": [m.to_dict() for m in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_memory(self, memory_id: str, current_user_id: str) -> AIMemory:
        """Retrieve single memory ensuring ownership."""
        memory = self.memory_repo.get_by_id(memory_id)
        if not memory:
            raise NotFoundException("Memory not found")
        check_resource_ownership(memory.user_id, current_user_id)
        return memory

    def create_memory(
        self,
        user_id: str,
        memory_key: str,
        memory_value: str,
        memory_type: str = "fact",
        confidence: float = 1.0,
        status: str = "confirmed",
        source_conversation_id: Optional[str] = None,
        source_message_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> AIMemory:
        """Manually create a confirmed memory."""
        if memory_type not in VALID_MEMORY_CATEGORIES:
            raise BadRequestException(f"Invalid category. Must be one of {VALID_MEMORY_CATEGORIES}")

        return self.memory_repo.create_memory(
            user_id=user_id,
            memory_key=memory_key,
            memory_value=memory_value,
            memory_type=memory_type,
            confidence=confidence,
            status=status,
            source_conversation_id=source_conversation_id,
            source_message_id=source_message_id,
            expires_at=expires_at
        )

    def update_memory(
        self,
        memory_id: str,
        current_user_id: str,
        updates: Dict[str, Any]
    ) -> AIMemory:
        """Edit an existing memory record."""
        memory = self.get_memory(memory_id, current_user_id)

        if "memory_type" in updates and updates["memory_type"] not in VALID_MEMORY_CATEGORIES:
            raise BadRequestException(f"Invalid category. Must be one of {VALID_MEMORY_CATEGORIES}")

        return self.memory_repo.update_memory(memory, updates)

    def delete_memory(self, memory_id: str, current_user_id: str) -> None:
        """Permanently delete a memory record."""
        memory = self.get_memory(memory_id, current_user_id)
        self.memory_repo.delete_memory(memory)

    def approve_suggestion(
        self,
        memory_id: str,
        current_user_id: str,
        edited_key: Optional[str] = None,
        edited_value: Optional[str] = None,
        edited_type: Optional[str] = None,
        supersede_existing_id: Optional[str] = None
    ) -> AIMemory:
        """Promote a pending suggestion to confirmed memory, optionally archiving/superseding a contradicted existing memory."""
        memory = self.get_memory(memory_id, current_user_id)
        if memory.status != "pending":
            raise BadRequestException(f"Cannot approve memory with status '{memory.status}'")

        # If user confirmed superseding an existing contradicted memory
        target_supersede = supersede_existing_id
        if not target_supersede and memory.embedding and isinstance(memory.embedding, dict):
            contra_info = memory.embedding.get("contradiction", {})
            target_supersede = contra_info.get("contradicting_memory_id")

        if target_supersede:
            old_mem = self.memory_repo.get_by_id(target_supersede)
            if old_mem and old_mem.user_id == current_user_id and old_mem.status == "confirmed":
                self.memory_repo.update_memory(old_mem, {"status": "archived"})

        updates: Dict[str, Any] = {"status": "confirmed"}
        if edited_key:
            updates["memory_key"] = edited_key.strip()[:100]
        if edited_value:
            updates["memory_value"] = edited_value.strip()
        if edited_type:
            if edited_type not in VALID_MEMORY_CATEGORIES:
                raise BadRequestException(f"Invalid category: {edited_type}")
            updates["memory_type"] = edited_type

        return self.memory_repo.update_memory(memory, updates)

    def reject_suggestion(self, memory_id: str, current_user_id: str) -> None:
        """Reject and delete a pending suggestion."""
        memory = self.get_memory(memory_id, current_user_id)
        # Deleting rejected suggestion avoids database bloat
        self.memory_repo.delete_memory(memory)

    def archive_memory(self, memory_id: str, current_user_id: str) -> AIMemory:
        """Archive a confirmed memory so it is excluded from future retrieval."""
        memory = self.get_memory(memory_id, current_user_id)
        return self.memory_repo.update_memory(memory, {"status": "archived"})

    def extract_and_store_candidates(
        self,
        user_id: str,
        user_message: str,
        assistant_response: Optional[str] = None,
        source_conversation_id: Optional[str] = None,
        source_message_id: Optional[str] = None
    ) -> List[AIMemory]:
        """Extract candidate suggestions, check for duplicates and contradictions, and persist strictly as pending."""
        from app.ai.memory.comparison import memory_comparison_engine

        candidates = self.extractor.extract_candidates(user_message, assistant_response)
        if not candidates:
            return []

        # Retrieve user's existing confirmed and pending memories to check duplicates/contradictions
        existing_memories, _ = self.memory_repo.list_for_user(
            user_id=user_id,
            status="confirmed",
            limit=100
        )
        pending_memories, _ = self.memory_repo.list_for_user(
            user_id=user_id,
            status="pending",
            limit=100
        )
        all_user_memories = existing_memories + pending_memories

        persisted = []

        for c in candidates:
            comp_result = memory_comparison_engine.check_duplicate_or_contradiction(
                candidate_key=c["memory_key"],
                candidate_value=c["memory_value"],
                candidate_type=c["memory_type"],
                existing_memories=all_user_memories
            )

            # Skip exact or near duplicates
            if comp_result["is_duplicate"]:
                continue

            # If contradiction detected, annotate the pending memory metadata for user review
            embedding_metadata = {}
            if comp_result["is_contradiction"]:
                embedding_metadata["contradiction"] = {
                    "contradicting_memory_id": comp_result["contradicting_memory_id"],
                    "reason": comp_result["contradiction_reason"],
                    "is_update_candidate": True,
                }

            mem = self.memory_repo.create_memory(
                user_id=user_id,
                memory_key=c["memory_key"],
                memory_value=c["memory_value"],
                memory_type=c["memory_type"],
                confidence=c["confidence"],
                status="pending",
                source_conversation_id=source_conversation_id,
                source_message_id=source_message_id,
                embedding=embedding_metadata if embedding_metadata else None
            )
            persisted.append(mem)
            all_user_memories.append(mem)

        return persisted

    def get_settings(self, user_id: str) -> Dict[str, Any]:
        """Retrieve memory personalization settings."""
        enabled = self.memory_repo.get_user_memory_preference(user_id)
        return {
            "ai_memory_enabled": enabled,
            "privacy_notice": "Memories are saved locally on your device. Only confirmed memories are used by the AI."
        }

    def update_settings(self, user_id: str, enabled: bool) -> Dict[str, Any]:
        """Update memory personalization toggle."""
        result = self.memory_repo.set_user_memory_preference(user_id, enabled)
        return {
            "ai_memory_enabled": result,
            "message": "Memory settings updated successfully"
        }

