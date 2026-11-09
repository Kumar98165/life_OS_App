"""LifeOS - AI Dataset Repository Layer (Step 7).

Data access operations for AITrainingSample curation and AIDatasetVersion snapshots.
"""
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import desc, func
from app.extensions import db
from app.models.ai import AITrainingSample, AIDatasetVersion, AIFeedback, AIMessage


class AIDatasetRepository:
    """Repository handling database queries and persistence for dataset curation and versioning."""

    def get_sample_by_id(self, sample_id: str) -> Optional[AITrainingSample]:
        """Fetch sample by primary key ID."""
        return db.session.get(AITrainingSample, sample_id)

    def list_samples(
        self,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        validation_status: Optional[str] = None,
        sanitization_status: Optional[str] = None,
        review_status: Optional[str] = None,
        consent_status: Optional[str] = None,
        dataset_version_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[AITrainingSample], int]:
        """Query and paginate training samples with flexible filtering."""
        query = AITrainingSample.query

        if user_id:
            query = query.filter(AITrainingSample.user_id == user_id)
        if category:
            query = query.filter(AITrainingSample.category == category)
        if validation_status:
            query = query.filter(AITrainingSample.validation_status == validation_status)
        if sanitization_status:
            query = query.filter(AITrainingSample.sanitization_status == sanitization_status)
        if review_status:
            query = query.filter(AITrainingSample.review_status == review_status)
        if consent_status:
            query = query.filter(AITrainingSample.consent_status == consent_status)
        if dataset_version_id:
            query = query.filter(AITrainingSample.dataset_version_id == dataset_version_id)

        total = query.count()
        items = (
            query
            .order_by(desc(AITrainingSample.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def update_sample_review(
        self,
        sample: AITrainingSample,
        review_status: str,
        quality_score: Optional[float] = None,
        validation_notes: Optional[str] = None
    ) -> AITrainingSample:
        """Update review decision on a candidate sample."""
        sample.review_status = review_status
        if quality_score is not None:
            sample.quality_score = quality_score
        if validation_notes is not None:
            sample.validation_notes = validation_notes
        sample.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return sample

    def delete_sample(self, sample: AITrainingSample) -> None:
        """Permanently remove a sample."""
        db.session.delete(sample)
        db.session.commit()

    def get_version_by_name(self, version_name: str) -> Optional[AIDatasetVersion]:
        """Fetch dataset version snapshot by unique version tag."""
        return AIDatasetVersion.query.filter_by(version_name=version_name).first()

    def get_version_by_id(self, version_id: str) -> Optional[AIDatasetVersion]:
        """Fetch dataset version snapshot by ID."""
        return db.session.get(AIDatasetVersion, version_id)

    def list_versions(self, limit: int = 20, offset: int = 0) -> Tuple[List[AIDatasetVersion], int]:
        """List dataset version snapshots."""
        query = AIDatasetVersion.query
        total = query.count()
        items = (
            query
            .order_by(desc(AIDatasetVersion.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def get_dataset_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Compute aggregate statistics on training sample population."""
        query = AITrainingSample.query
        if user_id:
            query = query.filter(AITrainingSample.user_id == user_id)

        total = query.count()
        approved = query.filter(AITrainingSample.review_status == "approved").count()
        pending_review = query.filter(AITrainingSample.review_status == "pending").count()
        rejected = query.filter(AITrainingSample.review_status == "rejected").count()

        valid_count = query.filter(AITrainingSample.validation_status == "valid").count()
        sanitized_count = query.filter(AITrainingSample.sanitization_status == "sanitized").count()
        consent_granted = query.filter(AITrainingSample.consent_status == "granted").count()

        category_counts = (
            db.session.query(AITrainingSample.category, func.count(AITrainingSample.id))
            .filter(AITrainingSample.category.isnot(None))
            .group_by(AITrainingSample.category)
            .all()
        )
        cat_map = {cat: count for cat, count in category_counts}

        return {
            "total_samples": total,
            "approved_count": approved,
            "pending_review_count": pending_review,
            "rejected_count": rejected,
            "valid_count": valid_count,
            "sanitized_count": sanitized_count,
            "consent_granted_count": consent_granted,
            "categories": cat_map,
        }
