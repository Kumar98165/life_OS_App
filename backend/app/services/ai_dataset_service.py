"""LifeOS - AI Dataset Management & Curation Service (Step 7).

Coordinates:
- Collection from user feedback & corrections
- PII & Secret Sanitization
- Quality & Compliance Validation
- Dataset Version Snapshot Creation (Manifest hashing & immutability)
- JSONL Export Formatting
"""
import json
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
from app.extensions import db
from app.models.ai import AITrainingSample, AIDatasetVersion, AIFeedback, AIMessage, AIConversation
from app.models.user_preference import UserPreference
from app.repositories.ai_dataset_repository import AIDatasetRepository
from app.ai.dataset.sanitizer import PrivacySanitizer
from app.ai.dataset.validator import DatasetQualityValidator
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException


class AIDatasetService:
    """Service layer for dataset collection, privacy sanitization, validation, and versioning."""

    def __init__(self, dataset_repo: Optional[AIDatasetRepository] = None):
        self.dataset_repo = dataset_repo or AIDatasetRepository()

    def collect_from_feedback(
        self,
        user_id: str,
        feedback_id: str
    ) -> Optional[AITrainingSample]:
        """Collect and transform eligible feedback into a candidate AITrainingSample.

        Enforces explicit user training consent. Respects consent revocation.
        Sanitizes text and executes deterministic quality validation.
        """
        # 1. Check user consent
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref or not pref.ai_training_consent:
            return None  # Cannot collect training data without explicit active consent

        # 2. Fetch feedback
        feedback = db.session.get(AIFeedback, feedback_id)
        if not feedback or str(feedback.user_id) != str(user_id):
            return None

        # 3. Fetch referenced message and its conversation prompt
        msg = db.session.get(AIMessage, feedback.message_id)
        if not msg:
            return None

        # Look up prompt input from previous user turn in conversation
        user_msg = (
            AIMessage.query
            .filter_by(conversation_id=msg.conversation_id, role="user")
            .filter(AIMessage.created_at <= msg.created_at)
            .order_by(AIMessage.created_at.desc())
            .first()
        )
        prompt_input = user_msg.content if user_msg else "General query"

        # Determine chosen and rejected responses
        dataset_type = "sft"
        rejected_response = None

        if feedback.suggested_response:
            # Correction provided by user
            chosen_response = feedback.suggested_response
            rejected_response = msg.content
            dataset_type = "dpo"
        elif feedback.rating == 1:
            # Positive thumbs up response
            chosen_response = msg.content
        else:
            # Negative feedback without correction cannot form an SFT target
            return None

        # 4. Privacy Sanitization
        sanitized = PrivacySanitizer.sanitize_sample(
            prompt_input=prompt_input,
            chosen_response=chosen_response,
            rejected_response=rejected_response
        )

        # 5. Quality Validation
        is_valid, validation_reasons = DatasetQualityValidator.validate_sample(
            prompt_input=sanitized["prompt_input"],
            chosen_response=sanitized["chosen_response"],
            consent_status="granted",
            sanitization_status=sanitized["sanitization_status"],
            category=feedback.category,
            rejected_response=sanitized["rejected_response"],
            quality_score=1.0,
            source_message_id=msg.id,
            source_feedback_id=feedback.id
        )

        validation_status = "valid" if is_valid else "invalid"
        validation_notes = "; ".join(validation_reasons) if validation_reasons else None

        # 6. Check if sample already collected for this feedback (idempotent)
        existing = AITrainingSample.query.filter_by(source_feedback_id=feedback.id).first()
        if existing:
            existing.prompt_input = sanitized["prompt_input"]
            existing.chosen_response = sanitized["chosen_response"]
            existing.rejected_response = sanitized["rejected_response"]
            existing.category = feedback.category
            existing.sanitization_status = sanitized["sanitization_status"]
            existing.validation_status = validation_status
            existing.validation_notes = validation_notes
            existing.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return existing

        sample = AITrainingSample(
            user_id=user_id,
            source_feedback_id=feedback.id,
            source_message_id=msg.id,
            prompt_input=sanitized["prompt_input"],
            chosen_response=sanitized["chosen_response"],
            rejected_response=sanitized["rejected_response"],
            category=feedback.category,
            dataset_type=dataset_type,
            consent_status="granted",
            review_status="approved" if is_valid else "pending",
            sanitization_status=sanitized["sanitization_status"],
            validation_status=validation_status,
            validation_notes=validation_notes,
            quality_score=1.0
        )
        db.session.add(sample)
        db.session.commit()
        return sample

    def review_sample(
        self,
        sample_id: str,
        review_status: str,
        quality_score: Optional[float] = None,
        validation_notes: Optional[str] = None
    ) -> AITrainingSample:
        """Approve or reject a sample record."""
        sample = self.dataset_repo.get_sample_by_id(sample_id)
        if not sample:
            raise NotFoundException("Training sample not found")

        return self.dataset_repo.update_sample_review(
            sample=sample,
            review_status=review_status,
            quality_score=quality_score,
            validation_notes=validation_notes
        )

    def delete_sample(self, sample_id: str) -> None:
        """Permanently remove an ineligible or invalid sample."""
        sample = self.dataset_repo.get_sample_by_id(sample_id)
        if not sample:
            raise NotFoundException("Training sample not found")

        self.dataset_repo.delete_sample(sample)

    def create_version_snapshot(
        self,
        version_name: str,
        description: Optional[str] = None,
        dataset_type: str = "sft",
        categories: Optional[List[str]] = None,
        created_by_user_id: Optional[str] = None
    ) -> AIDatasetVersion:
        """Create an immutable version snapshot of approved, validated, and sanitized records.

        Calculates a deterministic SHA-256 manifest hash over normalized JSON records.
        """
        # Ensure version name uniqueness
        if self.dataset_repo.get_version_by_name(version_name):
            raise BadRequestException(f"Dataset version '{version_name}' already exists.")

        # Query eligible approved samples:
        # - consent_status == 'granted'
        # - review_status == 'approved'
        # - validation_status == 'valid'
        # - sanitization_status == 'sanitized'
        query = AITrainingSample.query.filter(
            AITrainingSample.consent_status == "granted",
            AITrainingSample.review_status == "approved",
            AITrainingSample.validation_status == "valid",
            AITrainingSample.sanitization_status == "sanitized"
        )

        if dataset_type != "mixed":
            query = query.filter(AITrainingSample.dataset_type == dataset_type)

        if categories:
            query = query.filter(AITrainingSample.category.in_(categories))

        eligible_samples = query.order_by(AITrainingSample.created_at.asc()).all()

        if not eligible_samples:
            raise BadRequestException("No eligible approved and validated samples found to create version.")

        # Generate deterministic JSONL records to compute SHA-256 manifest hash
        jsonl_lines = []
        included_categories_set = set()

        for s in eligible_samples:
            record = {
                "id": s.id,
                "dataset_type": s.dataset_type,
                "prompt": s.prompt_input,
                "completion": s.chosen_response,
                "category": s.category,
                "quality_score": s.quality_score
            }
            if s.rejected_response:
                record["rejected_completion"] = s.rejected_response

            line_str = json.dumps(record, sort_keys=True, ensure_ascii=False)
            jsonl_lines.append(line_str)
            if s.category:
                included_categories_set.add(s.category)

        raw_manifest_payload = "\n".join(jsonl_lines).encode("utf-8")
        manifest_hash = hashlib.sha256(raw_manifest_payload).hexdigest()

        version = AIDatasetVersion(
            version_name=version_name,
            description=description,
            sample_count=len(eligible_samples),
            dataset_type=dataset_type,
            manifest_hash=manifest_hash,
            included_categories=list(included_categories_set),
            validation_summary={
                "total_samples": len(eligible_samples),
                "manifest_sha256": manifest_hash,
                "export_ready": True
            },
            is_exported=False,
            created_by=created_by_user_id
        )
        db.session.add(version)
        db.session.flush()

        # Link samples to this immutable version snapshot
        for s in eligible_samples:
            s.dataset_version_id = version.id

        db.session.commit()
        return version

    def export_version_jsonl(self, version_name: str) -> Tuple[str, str, Dict[str, Any]]:
        """Export a version snapshot as a validated JSONL string.

        Excludes records whose consent was revoked since snapshot creation.
        Returns:
            Tuple[jsonl_content, manifest_hash, metadata]
        """
        version = self.dataset_repo.get_version_by_name(version_name)
        if not version:
            raise NotFoundException(f"Dataset version '{version_name}' not found.")

        # Fetch samples linked to this version, verifying active consent
        samples = (
            AITrainingSample.query
            .filter_by(dataset_version_id=version.id)
            .filter(AITrainingSample.consent_status == "granted")
            .filter(AITrainingSample.review_status == "approved")
            .filter(AITrainingSample.sanitization_status == "sanitized")
            .order_by(AITrainingSample.created_at.asc())
            .all()
        )

        lines = []
        for s in samples:
            line_dict = {
                "sample_id": s.id,
                "prompt": s.prompt_input,
                "completion": s.chosen_response,
                "type": s.dataset_type,
                "quality_score": s.quality_score
            }
            if s.rejected_response:
                line_dict["rejected_completion"] = s.rejected_response

            lines.append(json.dumps(line_dict, sort_keys=True, ensure_ascii=False))

        export_content = "\n".join(lines)
        computed_hash = hashlib.sha256(export_content.encode("utf-8")).hexdigest()

        version.is_exported = True
        version.exported_at = datetime.now(timezone.utc)
        db.session.commit()

        metadata = {
            "version_name": version.version_name,
            "sample_count": len(samples),
            "manifest_hash": computed_hash,
            "exported_at": version.exported_at.isoformat()
        }

        return export_content, computed_hash, metadata
