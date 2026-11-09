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

    def chat_stream(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None
    ):
        """Process chat message and yield Server-Sent Events (SSE) while streaming tokens."""
        import json
        import time
        from app.ai.workflow import (
            node_retrieve_context,
            node_retrieve_memories,
            node_classify_intent,
            prepare_llm_messages,
            node_validate_response
        )
        from app.ai.config import get_llm
        from app.services.ai_prompt_service import AIPromptService
        from app.extensions import db

        cleaned_msg = message.strip()
        if not cleaned_msg:
            yield f"event: error\ndata: {json.dumps({'code': 'INVALID_REQUEST', 'message': 'Message cannot be empty'})}\n\n"
            return

        # 1. Resolve or create conversation
        try:
            is_new_thread = False
            if conversation_id:
                existing = self.ai_repo.get_by_id(conversation_id)
                if not existing:
                    yield f"event: error\ndata: {json.dumps({'code': 'NOT_FOUND', 'message': 'Conversation not found'})}\n\n"
                    return
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

            # 3. Load historical messages
            history_msgs = self.ai_repo.get_messages(conv.id, limit=8)
            prior_msgs = [m for m in history_msgs if m.id != user_msg.id]
            lc_history = []
            for m in prior_msgs:
                if m.role == "user":
                    lc_history.append(HumanMessage(content=m.content))
                elif m.role == "assistant":
                    lc_history.append(LcAIMessage(content=m.content))

            # 4. Resolve active prompt version
            prompt_service = AIPromptService()
            active_prompt = prompt_service.get_active_prompt_or_initialize()
            prompt_version_id = active_prompt.id if active_prompt else None
            prompt_template = active_prompt.prompt_template if active_prompt else None

            # Commit user turn to release active write lock before long inference
            db.session.commit()

        except Exception as setup_err:
            db.session.rollback()
            yield f"event: error\ndata: {json.dumps({'code': 'SETUP_ERROR', 'message': str(setup_err)})}\n\n"
            return

        # 5. Emit 'start' event with conversation metadata
        yield f"event: start\ndata: {json.dumps({'conversation_id': conv.id, 'conversation_title': conv.title})}\n\n"

        # 6. Execute LangGraph pre-inference nodes
        try:
            state = {
                "user_id": user_id,
                "user_message": cleaned_msg,
                "conversation_id": conv.id,
                "history": lc_history,
                "context_data": {},
                "formatted_context": "",
                "retrieved_memories": [],
                "formatted_memories": "",
                "memories_used": [],
                "intent": "",
                "response": "",
                "error": None,
                "prompt_template": prompt_template,
                "prompt_version_id": prompt_version_id,
            }

            ctx_res = node_retrieve_context(state)
            state.update(ctx_res)

            mem_res = node_retrieve_memories(state)
            state.update(mem_res)

            intent_res = node_classify_intent(state)
            state.update(intent_res)

            # Construct messages
            llm_messages = prepare_llm_messages(state)
            llm = get_llm()

        except Exception as prep_err:
            yield f"event: error\ndata: {json.dumps({'code': 'PREPARATION_ERROR', 'message': str(prep_err)})}\n\n"
            return

        # 7. Stream LLM tokens directly from Ollama with real-time safety boundary filtering
        accumulated_chunks = []
        start_t = time.perf_counter()

        # Prohibited token fragments that indicate prompt leakage or raw markup injection
        BLOCKED_FRAGMENTS = ["<user_input>", "</user_input>", "CORE GUIDELINES:", "SECURITY & INTEGRITY RULES:"]

        try:
            for chunk in llm.stream(llm_messages):
                token_text = chunk.content if hasattr(chunk, "content") else str(chunk)
                if token_text:
                    # Check if token attempts to inject or echo blocked boundary strings
                    is_blocked = any(frag in token_text for frag in BLOCKED_FRAGMENTS)
                    if is_blocked:
                        continue

                    accumulated_chunks.append(token_text)
                    yield f"event: token\ndata: {json.dumps({'content': token_text})}\n\n"

        except GeneratorExit:
            # Client disconnected or aborted stream prematurely
            db.session.rollback()
            return
        except Exception as stream_err:
            db.session.rollback()
            yield f"event: error\ndata: {json.dumps({'code': 'STREAM_ERROR', 'message': str(stream_err)})}\n\n"
            return

        total_latency_ms = int((time.perf_counter() - start_t) * 1000)
        raw_full_response = "".join(accumulated_chunks)

        # 8. Post-process & sanitize complete response
        state["response"] = raw_full_response
        validated_result = node_validate_response(state)
        final_clean_response = validated_result.get("response", raw_full_response)

        # 9. Persist completed assistant response
        try:
            assistant_msg = self.ai_repo.add_message(
                conversation_id=conv.id,
                role="assistant",
                content=final_clean_response,
                prompt_version_id=prompt_version_id,
                latency_ms=total_latency_ms
            )

            if is_new_thread or conv.title in ["New Conversation", "New Chat"]:
                new_title = _generate_title_from_query(cleaned_msg)
                self.ai_repo.update_title(conv, new_title)

            # Background memory extraction
            try:
                from app.services.ai_memory_service import AIMemoryService
                mem_svc = AIMemoryService()
                mem_svc.extract_and_store_candidates(
                    user_id=user_id,
                    user_message=cleaned_msg,
                    assistant_response=final_clean_response,
                    source_conversation_id=conv.id,
                    source_message_id=user_msg.id
                )
            except Exception:
                pass

            db.session.commit()

            # 10. Emit 'complete' event
            yield f"event: complete\ndata: {json.dumps({'message_id': assistant_msg.id, 'conversation_id': conv.id, 'latency_ms': total_latency_ms})}\n\n"

        except Exception as save_err:
            db.session.rollback()
            yield f"event: error\ndata: {json.dumps({'code': 'PERSISTENCE_ERROR', 'message': str(save_err)})}\n\n"


