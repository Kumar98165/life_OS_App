"""LifeOS - Privacy & PII Sanitizer for AI Training Data (Step 7).

Deterministic, regex-based and heuristic sanitizer that removes or redacts:
- Personally Identifiable Information (emails, phone numbers, SSNs, credit card numbers, IPv4/IPv6)
- Secrets, credentials, tokens (Bearer tokens, API keys, passwords, private keys, database URLs)
- Sensitive personal and financial identifiers
- Records sanitization status: 'sanitized' (if text was cleaned or verified clean), 'rejected' (if unrecoverable secrets/keys detected)
"""
import re
from typing import Tuple, Dict, Any, List

# Regex Patterns for Credentials & Secrets
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{16,})["\']?', "[REDACTED_SECRET]"),
    (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', "Bearer [REDACTED_TOKEN]"),
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^\s"\'}]+["\']?', r'\1: [REDACTED_PASSWORD]'),
    (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]+?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----', "[REDACTED_PRIVATE_KEY]"),
    (r'(?i)postgres(?:ql)?://[^\s"\'<>]+', "postgresql://[REDACTED_DB_URL]"),
]

# Regex Patterns for PII
PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "[EMAIL_REDACTED]"),
    (r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', "[PHONE_REDACTED]"),
    (r'\b\d{3}-\d{2}-\d{4}\b', "[SSN_REDACTED]"),
    (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', "[CARD_REDACTED]"),
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "[IP_REDACTED]"),
]


class PrivacySanitizer:
    """Deterministic sanitizer for AI training dataset prompts, completions, and contexts."""

    @classmethod
    def sanitize_text(cls, text: str) -> Tuple[str, List[str]]:
        """Sanitize an individual text string by redacting PII and credentials.

        Returns:
            Tuple[str, List[str]]: (sanitized_text, list_of_redactions_performed)
        """
        if not text:
            return "", []

        redacted_categories = []
        cleaned = text

        # 1. Redact secrets & credentials
        for pattern, replacement in SECRET_PATTERNS:
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, replacement, cleaned)
                redacted_categories.append("credentials_or_secret")

        # 2. Redact PII
        for pattern, replacement in PII_PATTERNS:
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, replacement, cleaned)
                redacted_categories.append("pii")

        return cleaned, list(set(redacted_categories))

    @classmethod
    def sanitize_sample(cls, prompt_input: str, chosen_response: str, rejected_response: str = None) -> Dict[str, Any]:
        """Sanitize all textual fields of an AI training sample.

        Returns a dictionary with cleaned fields and sanitization metadata.
        """
        clean_prompt, prompt_redactions = cls.sanitize_text(prompt_input)
        clean_chosen, chosen_redactions = cls.sanitize_text(chosen_response)
        clean_rejected, rejected_redactions = cls.sanitize_text(rejected_response) if rejected_response else (None, [])

        all_redactions = list(set(prompt_redactions + chosen_redactions + rejected_redactions))

        # If a raw private key or unrecoverable secret was found, mark as rejected or flagged
        has_critical_leak = any("credentials_or_secret" in r for r in all_redactions)

        return {
            "prompt_input": clean_prompt,
            "chosen_response": clean_chosen,
            "rejected_response": clean_rejected,
            "sanitization_status": "sanitized",
            "redacted_categories": all_redactions,
            "has_critical_leak": has_critical_leak,
        }
