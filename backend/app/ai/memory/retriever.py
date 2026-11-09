"""LifeOS - Memory Retrieval Engine.

Retrieves confirmed memories belonging to the authenticated user,
enforcing active validity, personalization preferences, and context budgeting.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, desc
from app.extensions import db
from app.models.ai import AIMemory
from app.models.user_preference import UserPreference


class MemoryRetrievalEngine:
    """Retrieves and scores relevant confirmed user memories for local AI context."""

    def is_personalization_enabled(self, user_id: str) -> bool:
        """Check user's memory personalization toggle in user_preferences."""
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if pref and not pref.ai_memory_enabled:
            return False
        return True

    def retrieve_relevant_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[AIMemory]:
        """Fetch confirmed, non-expired memories matching user query.

        Uses deterministic relevance ranking based on keyword matches,
        confidence, and recency of access. Updates last_accessed_at for retrieved items.
        """
        if not self.is_personalization_enabled(user_id):
            return []

        now = datetime.now(timezone.utc)

        # Base query: confirmed status, belongs to user, unexpired (and excludes rejected/pending/archived)
        base_query = AIMemory.query.filter(
            AIMemory.user_id == user_id,
            AIMemory.status == "confirmed",
            or_(AIMemory.expires_at.is_(None), AIMemory.expires_at > now)
        )

        if category and category != "all":
            base_query = base_query.filter(AIMemory.memory_type == category)

        memories = base_query.all()
        if not memories:
            return []

        # Deterministic keyword scoring
        tokens = set(re_tokenize(query.lower()))
        scored_memories = []

        for mem in memories:
            text_corpus = f"{mem.memory_key} {mem.memory_value} {mem.memory_type}".lower()
            score = 0.0

            # Match individual tokens
            for token in tokens:
                if len(token) > 2 and token in text_corpus:
                    score += 2.0

            # Bonus for confidence
            score += float(mem.confidence or 0.8)

            # Bonus for recency of confirmation or last access (within last 30 days)
            ref_dt = mem.last_accessed_at or mem.created_at
            if ref_dt:
                if ref_dt.tzinfo is None:
                    ref_dt = ref_dt.replace(tzinfo=timezone.utc)
                age_days = (now - ref_dt).total_seconds() / 86400.0
                if age_days < 7:
                    score += 1.0
                elif age_days < 30:
                    score += 0.5

            scored_memories.append((score, mem))

        # Sort descending by score, then recency
        scored_memories.sort(
            key=lambda x: (x[0], x[1].last_accessed_at or x[1].created_at or datetime.min),
            reverse=True
        )

        selected = [m for _, m in scored_memories[:limit]]

        # Touch last_accessed_at
        if selected:
            for m in selected:
                m.last_accessed_at = now
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return selected

    def format_memories_prompt(self, memories: List[AIMemory]) -> str:
        """Format retrieved memories into a clean markdown block for system prompt."""
        if not memories:
            return ""

        lines = [
            "### Confirmed User Memories (Personal Knowledge)",
            "The user has previously approved the following personal facts, preferences, and routines:",
        ]
        for m in memories:
            lines.append(f"- **{m.memory_key}** ({m.memory_type}): {m.memory_value}")
        lines.append("")
        return "\n".join(lines)


def re_tokenize(text: str) -> List[str]:
    """Helper tokenizer for simple deterministic keyword scoring."""
    import re
    return [t for t in re.split(r"[^\w]+", text) if t]

