"""LifeOS - AI Service Layer.

Coordinates conversation threads, message histories, LangGraph workflow execution,
and safe multi-turn local dialogue.
"""
from typing import Optional, List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage as LcAIMessage
from app.repositories.ai_repository import AIConversationRepository
from app.models.ai import AIConversation, AIMessage
from app.ai.workflow import lifeos_agent_graph
from app.ai.config import check_ollama_health, get_ai_config
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.security import check_resource_ownership


def _generate_title_from_query(query: str) -> str:
    """Generate a clean conversation title from the first message."""
    cleaned = query.strip().replace("\n", " ")
    words = cleaned.split()
    if not words:
        return "Conversation"
    title = " ".join(words[:6])
    return title[:60].capitalize()


class AIService:
    """Business service orchestrating local AI conversations, persistence, and LangGraph."""

    def __init__(self, ai_repo: Optional[AIConversationRepository] = None):
        self.ai_repo = ai_repo or AIConversationRepository()

    def get_health_status(self) -> Dict[str, Any]:
        """Check Ollama runtime health and model availability."""
        return check_ollama_health()

    def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> AIConversation:
        """Explicitly create a new conversation thread."""
        cfg = get_ai_config()
        return self.ai_repo.create_conversation(
            user_id=user_id,
            title=title or "New Conversation",
            model_used=cfg["model"]
        )

    def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List conversation threads for authenticated user."""
        conversations = self.ai_repo.list_for_user(user_id=user_id, limit=limit, offset=offset)
        return [c.to_dict() for c in conversations]

    def get_conversation_history(
        self,
        conversation_id: str,
        current_user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Retrieve conversation and full message list ensuring ownership."""
        conv = self.ai_repo.get_by_id(conversation_id)
        if not conv:
            raise NotFoundException("Conversation not found")

        check_resource_ownership(conv.user_id, current_user_id)
        messages = self.ai_repo.get_messages(conversation_id, limit=limit)

        return {
            "conversation": conv.to_dict(),
            "messages": [m.to_dict() for m in messages]
        }

    def delete_conversation(self, conversation_id: str, current_user_id: str) -> None:
        """Delete conversation ensuring ownership."""
        conv = self.ai_repo.get_by_id(conversation_id)
        if not conv:
            raise NotFoundException("Conversation not found")

        check_resource_ownership(conv.user_id, current_user_id)
        self.ai_repo.delete_conversation(conv)

    def chat(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process chat message through LangGraph and persist conversation turn."""
        cleaned_msg = message.strip()
        if not cleaned_msg:
            raise BadRequestException("Message cannot be empty")

        # 1. Resolve or create conversation
        conv: AIConversation
        is_new_thread = False
        if conversation_id:
            existing = self.ai_repo.get_by_id(conversation_id)
            if not existing:
                raise NotFoundException("Conversation not found")
            check_resource_ownership(existing.user_id, user_id)
            conv = existing
        else:
            conv = self.create_conversation(user_id)
            is_new_thread = True

        # 2. Persist user turn
        user_msg = self.ai_repo.add_message(
            conversation_id=conv.id,
            role="user",
            content=cleaned_msg
        )

        # 3. Load historical messages for context window
        history_msgs = self.ai_repo.get_messages(conv.id, limit=8)
        # Exclude the user turn we just added from history
        prior_msgs = [m for m in history_msgs if m.id != user_msg.id]

        lc_history = []
        for m in prior_msgs:
            if m.role == "user":
                lc_history.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                lc_history.append(LcAIMessage(content=m.content))

        # 4. Resolve active prompt version once for deterministic execution & attribution
        from app.services.ai_prompt_service import AIPromptService
        import time

        prompt_service = AIPromptService()
        active_prompt = prompt_service.get_active_prompt_or_initialize()
        prompt_version_id = active_prompt.id if active_prompt else None
        prompt_template = active_prompt.prompt_template if active_prompt else None

        initial_state = {
            "user_id": user_id,
            "user_message": cleaned_msg,
            "conversation_id": conv.id,
            "history": lc_history,
            "context_data": {},
            "formatted_context": "",
            "intent": "",
            "response": "",
            "error": None,
            "prompt_template": prompt_template,
            "prompt_version_id": prompt_version_id,
        }

        start_t = time.perf_counter()
        graph_result = lifeos_agent_graph.invoke(initial_state)
        latency_ms = int((time.perf_counter() - start_t) * 1000)
        assistant_content = graph_result.get("response", "")

        # 5. Persist assistant response turn with prompt attribution
        assistant_msg = self.ai_repo.add_message(
            conversation_id=conv.id,
            role="assistant",
            content=assistant_content,
            prompt_version_id=prompt_version_id,
            latency_ms=latency_ms
        )

        # 6. Dynamically rename conversation if initial generic title
        if is_new_thread or conv.title in ["New Conversation", "New Chat"]:
            new_title = _generate_title_from_query(cleaned_msg)
            self.ai_repo.update_title(conv, new_title)

        # 7. Safely extract candidate memories into 'pending' status for user review
        memories_extracted = []
        try:
            from app.services.ai_memory_service import AIMemoryService
            memory_service = AIMemoryService()
            stored = memory_service.extract_and_store_candidates(
                user_id=user_id,
                user_message=cleaned_msg,
                assistant_response=assistant_content,
                source_conversation_id=conv.id,
                source_message_id=user_msg.id
            )
            memories_extracted = [m.to_dict() for m in stored]
        except Exception:
            # Extraction failure must never interrupt the user's chat flow
            pass

        return {
            "conversation_id": conv.id,
            "conversation_title": conv.title,
            "message_id": assistant_msg.id,
            "user_message": user_msg.to_dict(),
            "assistant_message": assistant_msg.to_dict(),
            "response": assistant_content,
            "intent": graph_result.get("intent", "general_chat"),
            "memories_used": graph_result.get("memories_used", []),
            "memories_extracted": memories_extracted,
        }

