"""LifeOS - Integrated Voice Assistant Orchestrator.

Ties together:
1. Audio Input Validation & Local STT (`stt_service`)
2. Context Retrieval & Prompt Construction
3. Local Ollama LLM / LangGraph Agent & Tool Registry
4. Human Approval Gate for medium/high risk operations
5. Action Execution
6. Response Formatting
7. Local TTS Audio Synthesis (`tts_service`)
"""
import base64
import logging
from typing import Dict, Any, Optional, Tuple
from app.services.voice.stt_service import stt_service
from app.services.voice.tts_service import tts_service
from app.services.ai_service import AIService
from app.services.automation_service import AutomationService
from app.models.automation import AutomationApproval
from app.models.voice import VoicePreference
from app.extensions import db

logger = logging.getLogger(__name__)


class VoiceAssistantService:
    """End-to-End Voice Assistant Pipeline."""

    def __init__(self):
        self.ai_service = AIService()
        self.automation_service = AutomationService()

    def get_or_create_voice_preferences(self, user_id: str) -> VoicePreference:
        """Fetch or initialize default voice settings for a user."""
        pref = VoicePreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = VoicePreference(
                user_id=user_id,
                language="en",
                voice_name="default",
                speech_rate=1.0,
                speech_pitch=1.0,
                auto_play_response=True,
                audio_privacy_enabled=True,
                confirm_actions_via_voice=True
            )
            db.session.add(pref)
            db.session.commit()
        return pref

    def process_voice_turn(
        self,
        user_id: str,
        audio_stream_or_bytes: Optional[Any] = None,
        filename: str = "voice.wav",
        text_input: Optional[str] = None,
        conversation_id: Optional[str] = None,
        return_audio: bool = True
    ) -> Dict[str, Any]:
        """Process a complete voice turn.

        Pipeline:
        1. Transcribe audio if provided (or use text_input fallback).
        2. Retrieve user's voice settings.
        3. Pass query to LifeOS AI Assistant / LangGraph Agent.
        4. Detect if proposed actions require human confirmation.
        5. Generate spoken response text.
        6. Synthesize TTS audio if requested.
        7. Return structured turn output.

        Args:
            user_id: The authenticated user's ID.
            audio_stream_or_bytes: Raw audio data or file stream.
            filename: Audio filename with extension.
            text_input: Direct text prompt (fallback when mic isn't used).
            conversation_id: Optional AI conversation ID for context continuity.
            return_audio: Whether to generate TTS audio bytes.

        Returns:
            Dict containing transcript, response_text, audio_base64, action_proposals, etc.
        """
        # Step 1: Voice transcription (STT)
        transcription_result = None
        user_prompt = ""

        if audio_stream_or_bytes is not None:
            transcription_result = stt_service.transcribe_file(
                audio_stream_or_bytes=audio_stream_or_bytes,
                filename=filename
            )
            user_prompt = transcription_result.get("text", "").strip()
        elif text_input:
            user_prompt = text_input.strip()
        else:
            raise ValueError("Either an audio file or text_input must be provided.")

        if not user_prompt:
            return {
                "transcript": "",
                "detected_language": transcription_result.get("detected_language") if transcription_result else "en",
                "response_text": "I didn't hear anything. Please try speaking again.",
                "actions": [],
                "requires_approval": False,
                "audio_base64": None,
                "conversation_id": conversation_id
            }

        # Step 2: Fetch user preferences
        voice_prefs = self.get_or_create_voice_preferences(user_id)
        preferred_lang = voice_prefs.language

        # Step 3: Run AI Assistant chat
        # Prepend voice context instruction to keep response concise and spoken-friendly
        ai_response = self.ai_service.chat(
            user_id=user_id,
            message=user_prompt,
            conversation_id=conversation_id
        )

        reply_text = ai_response.get("response") or ai_response.get("reply") or ""
        conv_id = ai_response.get("conversation_id", conversation_id)

        # Step 4: Check for pending automations/actions requiring approval
        pending_approvals = AutomationApproval.query.filter_by(
            user_id=user_id,
            status="pending"
        ).order_by(AutomationApproval.created_at.desc()).all()

        recent_approval = None
        requires_approval = False
        action_proposals = []

        if pending_approvals:
            recent_approval = pending_approvals[0]
            requires_approval = True
            action_proposals.append({
                "approval_id": recent_approval.id,
                "action_type": recent_approval.action.action_type if recent_approval.action else "action",
                "risk_level": recent_approval.risk_level,
                "summary": recent_approval.summary,
                "parameters": recent_approval.action.parameters if recent_approval.action else {}
            })

            # Append voice confirmation prompt if appropriate
            if voice_prefs.confirm_actions_via_voice:
                confirm_prompt = f" This action requires your confirmation: {recent_approval.summary}. Would you like me to proceed?"
                if not reply_text.endswith("?"):
                    reply_text = f"{reply_text}{confirm_prompt}"

        # Step 5: Synthesize speech if audio requested
        audio_base64 = None
        if return_audio and reply_text:
            tts_lang = "hi" if preferred_lang == "hi" or (transcription_result and transcription_result.get("detected_language") == "hi") else "en"
            wav_bytes = tts_service.synthesize_to_wav_bytes(
                text=reply_text,
                language=tts_lang,
                speech_rate=voice_prefs.speech_rate,
                voice_id=voice_prefs.voice_name if voice_prefs.voice_name != "default" else None
            )
            audio_base64 = base64.b64encode(wav_bytes).decode("utf-8")

        return {
            "transcript": user_prompt,
            "detected_language": transcription_result.get("detected_language") if transcription_result else "en",
            "language_probability": transcription_result.get("language_probability") if transcription_result else 1.0,
            "response_text": reply_text,
            "conversation_id": conv_id,
            "requires_approval": requires_approval,
            "action_proposals": action_proposals,
            "audio_base64": audio_base64,
            "audio_mime_type": "audio/wav" if audio_base64 else None
        }


# Global Voice Assistant orchestrator instance
voice_assistant_service = VoiceAssistantService()
