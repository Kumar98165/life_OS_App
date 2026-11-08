"""LifeOS - AI Blueprint Routes.

Endpoints for chat interactions, conversation management,
and local Ollama health monitoring.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.ai import ChatRequest, CreateConversationRequest
from app.services.ai_service import AIService
from app.core.response import api_response

ai_bp = Blueprint("ai", __name__)
ai_service = AIService()


# ---------------------------------------------------------
# Health / Diagnostics
# ---------------------------------------------------------

@ai_bp.route("/health", methods=["GET"])
def get_ai_health():
    """Check Ollama runtime connection and model status."""
    status_info = ai_service.get_health_status()
    code = 200 if status_info.get("healthy") else 503
    return api_response(
        data=status_info,
        message="Local AI runtime status",
        status_code=code
    )


# ---------------------------------------------------------
# Chat Execution
# ---------------------------------------------------------

@ai_bp.route("/chat", methods=["POST"])
@jwt_required()
def send_chat_message():
    """Send a prompt to the AI Assistant and receive a context-aware response."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = ChatRequest(**json_data)

    chat_result = ai_service.chat(
        user_id=user_id,
        message=validated.message,
        conversation_id=validated.conversation_id
    )

    return api_response(
        data=chat_result,
        message="AI response generated successfully",
        status_code=200
    )


# ---------------------------------------------------------
# Conversation Management
# ---------------------------------------------------------

@ai_bp.route("/conversations", methods=["POST"])
@jwt_required()
def create_conversation():
    """Create a new conversation thread."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateConversationRequest(**json_data)

    conv = ai_service.create_conversation(user_id=user_id, title=validated.title)

    return api_response(
        data={"conversation": conv.to_dict()},
        message="Conversation created successfully",
        status_code=201
    )


@ai_bp.route("/conversations", methods=["GET"])
@jwt_required()
def list_conversations():
    """List conversation threads for authenticated user."""
    user_id = get_jwt_identity()
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    conversations = ai_service.list_conversations(user_id=user_id, limit=limit, offset=offset)

    return api_response(
        data={"conversations": conversations},
        message="Conversations retrieved successfully"
    )


@ai_bp.route("/conversations/<conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation_history(conversation_id: str):
    """Retrieve full history of a conversation thread."""
    user_id = get_jwt_identity()
    limit = request.args.get("limit", 50, type=int)

    history = ai_service.get_conversation_history(
        conversation_id=conversation_id,
        current_user_id=user_id,
        limit=limit
    )

    return api_response(
        data=history,
        message="Conversation history retrieved successfully"
    )


@ai_bp.route("/conversations/<conversation_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation(conversation_id: str):
    """Delete a conversation thread and its messages."""
    user_id = get_jwt_identity()
    ai_service.delete_conversation(conversation_id=conversation_id, current_user_id=user_id)

    return api_response(
        data=None,
        message="Conversation deleted successfully"
    )

