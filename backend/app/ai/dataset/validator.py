"""LifeOS - Training Dataset Quality Validator (Step 7).

Deterministic Python quality validation ensuring only clean, well-formed,
consented, and high-quality instruction-tuning records are approved for export.
"""
from typing import Dict, Any, List, Tuple
from app.schemas.ai_feedback import SUPPORTED_FEEDBACK_CATEGORIES

# Quality Constants
MIN_PROMPT_LEN = 3
MAX_PROMPT_LEN = 4000
MIN_RESPONSE_LEN = 3
MAX_RESPONSE_LEN = 6000
MIN_QUALITY_SCORE = 0.5


class DatasetQualityValidator:
    """Validates training sample records before approval and dataset snapshot export."""

    @classmethod
    def validate_sample(
        cls,
        prompt_input: str,
        chosen_response: str,
        consent_status: str,
        sanitization_status: str,
        category: str = None,
        rejected_response: str = None,
        quality_score: float = 1.0,
        source_message_id: str = None,
        source_feedback_id: str = None,
    ) -> Tuple[bool, List[str]]:
        """Run deterministic quality and compliance checks on a training sample.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_validation_reasons)
        """
        reasons = []

        # 1. Consent Verification
        if consent_status != "granted":
            reasons.append(f"Invalid consent status: '{consent_status}'. Must be 'granted'.")

        # 2. Sanitization Check
        if sanitization_status != "sanitized":
            reasons.append(f"Record has not passed privacy sanitization (status: '{sanitization_status}').")

        # 3. Non-empty Prompt & Chosen Response
        clean_prompt = (prompt_input or "").strip()
        clean_chosen = (chosen_response or "").strip()

        if not clean_prompt:
            reasons.append("Empty prompt input.")
        elif len(clean_prompt) < MIN_PROMPT_LEN:
            reasons.append(f"Prompt is too short (< {MIN_PROMPT_LEN} characters).")
        elif len(clean_prompt) > MAX_PROMPT_LEN:
            reasons.append(f"Prompt exceeds maximum character length of {MAX_PROMPT_LEN}.")

        if not clean_chosen:
            reasons.append("Empty chosen response.")
        elif len(clean_chosen) < MIN_RESPONSE_LEN:
            reasons.append(f"Chosen response is too short (< {MIN_RESPONSE_LEN} characters).")
        elif len(clean_chosen) > MAX_RESPONSE_LEN:
            reasons.append(f"Chosen response exceeds maximum character length of {MAX_RESPONSE_LEN}.")

        # 4. Prompt vs Response Trivial Duplication
        if clean_prompt.lower() == clean_chosen.lower() and len(clean_prompt) > 0:
            reasons.append("Degenerate sample: chosen response is an exact copy of the prompt input.")

        # 5. DPO-specific checks (if rejected response provided)
        if rejected_response:
            clean_rejected = rejected_response.strip()
            if clean_rejected.lower() == clean_chosen.lower():
                reasons.append("DPO pair invalid: chosen and rejected responses are identical.")

        # 6. Category validation if specified
        if category and category not in SUPPORTED_FEEDBACK_CATEGORIES:
            reasons.append(f"Invalid category '{category}'. Must be one of {SUPPORTED_FEEDBACK_CATEGORIES}")

        # 7. Quality Score threshold
        if quality_score < MIN_QUALITY_SCORE:
            reasons.append(f"Quality score {quality_score:.2f} is below minimum threshold {MIN_QUALITY_SCORE:.2f}.")

        # 8. Source Traceability
        if not source_message_id and not source_feedback_id:
            reasons.append("Missing source traceability: sample must reference either source_message_id or source_feedback_id.")

        is_valid = len(reasons) == 0
        return is_valid, reasons
