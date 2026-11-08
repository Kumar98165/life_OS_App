"""LifeOS - Memory Extraction Engine.

Analyzes dialogue messages to identify high-value long-term candidate memories
(preferences, personal context, confirmed goals/decisions, routine patterns, facts).
Adheres strictly to local execution and privacy boundaries, saving all candidates
in 'pending' status for explicit user approval.
"""
import json
import re
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.config import get_llm
from app.models.ai import AIMemory

# Categories supported
VALID_MEMORY_CATEGORIES = [
    "preference",
    "personal_context",
    "goal_decision",
    "routine_pattern",
    "fact",
]

# Sensitive patterns that must never be committed to memory
SENSITIVE_PATTERNS = [
    r"(?i)(password|passwd|secret|api[_-]?key|token|bearer|jwt)",
    r"(?i)(credit[\s_-]?card|cvv|cvc|ssn|social security|bank account)",
    r"(?i)(private key|access[_-]?secret|auth[_-]?code)",
]

EXTRACTION_SYSTEM_PROMPT = """You are LifeOS Memory Extractor, a local background analyzer.
Your task is to identify important, persistent long-term personal facts, preferences, goals, or routines explicitly mentioned by the user in this message.

ALLOWED CATEGORIES:
- preference: Preferred communication style, focus times, or work preferences.
- personal_context: Long-term background, career role, or confirmed tools.
- goal_decision: Confirmed long-term goals, milestones, or important decisions.
- routine_pattern: Confirmed daily routines, sleep habits, or recurring schedules.
- fact: Factual user information useful across future conversations.

STRICT PRIVACY RULES:
1. NEVER extract passwords, API keys, credentials, secret codes, credit cards, or financial account details.
2. If the user message is trivial (greetings, short questions, momentary queries like "what time is it"), return an empty list.
3. Extract ONLY facts explicitly stated by the user. Do not invent or assume.
4. Output MUST be a valid JSON array of objects with the keys:
   - "memory_key": Short title (max 50 chars, e.g. "Prefers morning focus sessions")
   - "memory_value": Clear factual statement (e.g. "User does best focused work between 9 AM and 11 AM.")
   - "memory_type": One of [preference, personal_context, goal_decision, routine_pattern, fact]
   - "confidence": Float between 0.7 and 1.0

Return ONLY the raw JSON array. If nothing should be remembered, return [].
"""


def _is_sensitive_content(text: str) -> bool:
    """Check if content matches sensitive data patterns."""
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def _is_trivial_message(text: str) -> bool:
    """Filter out trivial greetings, confirmations, and short queries."""
    trimmed = text.strip().lower()
    if len(trimmed) < 10:
        return True
    trivial_phrases = [
        "hello", "hi", "hey", "good morning", "good evening", "thanks", "thank you",
        "ok", "okay", "bye", "goodbye", "cool", "great", "nice", "yes", "no"
    ]
    if trimmed in trivial_phrases:
        return True
    return False


class MemoryExtractionEngine:
    """Extracts candidate memory suggestions from user dialogue turns."""

    def extract_candidates(
        self,
        user_message: str,
        assistant_response: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Run local Qwen model to extract candidate memories from user input."""
        cleaned = user_message.strip()
        if _is_trivial_message(cleaned) or _is_sensitive_content(cleaned):
            return []

        prompt_input = f"User said: {cleaned}"
        if assistant_response:
            prompt_input += f"\nAssistant responded: {assistant_response[:300]}"

        try:
            llm = get_llm(temperature=0.1)
            messages = [
                SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
                HumanMessage(content=prompt_input)
            ]
            result = llm.invoke(messages)
            raw_text = result.content if hasattr(result, "content") else str(result)

            # Extract JSON block
            json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            if not json_match:
                return []

            parsed = json.loads(json_match.group(0))
            if not isinstance(parsed, list):
                return []

            candidates = []
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                key = str(item.get("memory_key", "")).strip()[:100]
                val = str(item.get("memory_value", "")).strip()
                mtype = str(item.get("memory_type", "fact")).lower()
                conf = float(item.get("confidence", 0.8))

                if not key or not val:
                    continue
                if mtype not in VALID_MEMORY_CATEGORIES:
                    mtype = "fact"
                if _is_sensitive_content(val) or _is_sensitive_content(key):
                    continue

                candidates.append({
                    "memory_key": key,
                    "memory_value": val,
                    "memory_type": mtype,
                    "confidence": max(0.5, min(1.0, conf)),
                    "status": "pending",  # Strict requirement: all candidates start as pending
                })

            return candidates

        except Exception:
            return []
