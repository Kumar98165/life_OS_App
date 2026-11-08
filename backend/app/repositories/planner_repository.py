from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import func, asc
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.planner import PlannerBlock
from app.core.pagination import paginate_query


class PlannerRepository:
    """Repository handling database operations and queries for planner blocks."""

    def create(
        self,
        user_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        block_type: str = "task",
        status: str = "scheduled",
        task_id: Optional[str] = None,
        color_hex: Optional[str] = None
    ) -> PlannerBlock:
        """Create and persist a new planner block."""
        is_completed = (status == "completed")
        block = PlannerBlock(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            block_type=block_type,
            status=status,
            task_id=task_id,
            color_hex=color_hex,
            is_completed=is_completed
        )
        db.session.add(block)
        db.session.commit()
        return block

    def get_by_id(self, block_id: str) -> Optional[PlannerBlock]:
        """Retrieve a planner block by ID with eager-loaded task relationship."""
        return (
            PlannerBlock.query
            .options(joinedload(PlannerBlock.task))
            .filter_by(id=block_id)
            .first()
        )

    def check_conflict(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_block_id: Optional[str] = None
    ) -> Optional[PlannerBlock]:
        """
        Detect any overlapping planner block for the same user.
        Two intervals [A_start, A_end] and [B_start, B_end] overlap iff:
            A_start < B_end AND A_end > B_start
        Adjacent blocks (e.g. 09:00-10:00 and 10:00-11:00) do NOT overlap.
        Cancelled blocks are excluded because they do not reserve active time.
        """
        query = PlannerBlock.query.filter(
            PlannerBlock.user_id == user_id,
            PlannerBlock.status != "cancelled",
            PlannerBlock.start_time < end_time,
            PlannerBlock.end_time > start_time
        )

        if exclude_block_id:
            query = query.filter(PlannerBlock.id != exclude_block_id)

        return query.first()

    def list_for_user(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        block_type: Optional[str] = None,
        task_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[PlannerBlock], Dict[str, Any]]:
        """List planner blocks for user with date-range filters and pagination."""
        query = (
            PlannerBlock.query
            .options(joinedload(PlannerBlock.task))
            .filter(PlannerBlock.user_id == user_id)
        )

        if start_date:
            query = query.filter(PlannerBlock.end_time >= start_date)
        if end_date:
            query = query.filter(PlannerBlock.start_time <= end_date)
        if status:
            query = query.filter(PlannerBlock.status == status)
        if block_type:
            query = query.filter(PlannerBlock.block_type == block_type)
        if task_id:
            query = query.filter(PlannerBlock.task_id == task_id)

        query = query.order_by(asc(PlannerBlock.start_time))
        return paginate_query(query, page, per_page)

    def update(self, block: PlannerBlock, **kwargs) -> PlannerBlock:
        """Update planner block fields and commit."""
        for field, value in kwargs.items():
            if hasattr(block, field) and value is not None:
                setattr(block, field, value)

        if "status" in kwargs and kwargs["status"] is not None:
            block.is_completed = (kwargs["status"] == "completed")

        db.session.commit()
        return block

    def delete(self, block: PlannerBlock) -> None:
        """Delete a planner block."""
        db.session.delete(block)
        db.session.commit()

    def get_daily_summary(
        self,
        user_id: str,
        day_start: datetime,
        day_end: datetime,
        now_utc: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Aggregate summary metrics for a specified day window."""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        blocks = (
            PlannerBlock.query
            .options(joinedload(PlannerBlock.task))
            .filter(
                PlannerBlock.user_id == user_id,
                PlannerBlock.start_time >= day_start,
                PlannerBlock.start_time <= day_end
            )
            .order_by(asc(PlannerBlock.start_time))
            .all()
        )

        total_blocks = len(blocks)
        completed_blocks = sum(1 for b in blocks if b.status == "completed" or b.is_completed)
        scheduled_blocks = sum(1 for b in blocks if b.status == "scheduled")
        cancelled_blocks = sum(1 for b in blocks if b.status == "cancelled")
        skipped_blocks = sum(1 for b in blocks if b.status == "skipped")

        def _as_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        total_scheduled_minutes = sum(
            int((_as_utc(b.end_time) - _as_utc(b.start_time)).total_seconds() / 60)
            for b in blocks
            if b.status != "cancelled"
        )

        # Earliest upcoming block today that hasn't started or is currently in progress
        upcoming_blocks = [
            b for b in blocks
            if _as_utc(b.end_time) > now_utc and b.status == "scheduled"
        ]
        next_block = upcoming_blocks[0].to_dict() if upcoming_blocks else None

        return {
            "date": day_start.date().isoformat(),
            "total_blocks": total_blocks,
            "completed_blocks": completed_blocks,
            "scheduled_blocks": scheduled_blocks,
            "cancelled_blocks": cancelled_blocks,
            "skipped_blocks": skipped_blocks,
            "total_scheduled_minutes": total_scheduled_minutes,
            "completion_rate": round((completed_blocks / total_blocks * 100), 1) if total_blocks > 0 else 0.0,
            "next_upcoming_block": next_block,
            "blocks": [b.to_dict() for b in blocks]
        }
