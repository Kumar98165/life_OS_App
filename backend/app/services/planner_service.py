from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from app.repositories.planner_repository import PlannerRepository
from app.repositories.task_repository import TaskRepository
from app.models.planner import PlannerBlock
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException
from app.core.security import check_resource_ownership


class PlannerService:
    """Business service coordinating daily planner operations, time validations, and conflict prevention."""

    def __init__(
        self,
        planner_repo: Optional[PlannerRepository] = None,
        task_repo: Optional[TaskRepository] = None
    ):
        self.planner_repo = planner_repo or PlannerRepository()
        self.task_repo = task_repo or TaskRepository()

    def create_block(
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
        """Create a new planner block with conflict detection and task ownership verification."""
        # Normalize datetimes to UTC timezone-aware
        start_utc = self._ensure_utc(start_time)
        end_utc = self._ensure_utc(end_time)

        if start_utc >= end_utc:
            raise BadRequestException("start_time must be strictly earlier than end_time")

        # Validate linked task if provided
        if task_id:
            task = self.task_repo.get_by_id(task_id)
            if not task:
                raise NotFoundException("Linked task not found")
            if task.user_id != user_id:
                raise BadRequestException("Linked task does not belong to the authenticated user")

        # Check for scheduling conflicts (only active scheduled/completed blocks)
        if status != "cancelled":
            conflict = self.planner_repo.check_conflict(
                user_id=user_id,
                start_time=start_utc,
                end_time=end_utc
            )
            if conflict:
                raise ConflictException(
                    f"Scheduling conflict with existing block '{conflict.title}' "
                    f"from {conflict.start_time.strftime('%H:%M')} to {conflict.end_time.strftime('%H:%M')}"
                )

        return self.planner_repo.create(
            user_id=user_id,
            title=title,
            start_time=start_utc,
            end_time=end_utc,
            description=description,
            block_type=block_type,
            status=status,
            task_id=task_id,
            color_hex=color_hex
        )

    def get_block(self, block_id: str, current_user_id: str) -> PlannerBlock:
        """Retrieve a planner block by ID, strictly enforcing resource ownership."""
        block = self.planner_repo.get_by_id(block_id)
        if not block:
            raise NotFoundException("Planner block not found")

        check_resource_ownership(block.user_id, current_user_id)
        return block

    def list_blocks(
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
        """List user's planner blocks with filters and pagination."""
        start_utc = self._ensure_utc(start_date) if start_date else None
        end_utc = self._ensure_utc(end_date) if end_date else None

        return self.planner_repo.list_for_user(
            user_id=user_id,
            start_date=start_utc,
            end_date=end_utc,
            status=status,
            block_type=block_type,
            task_id=task_id,
            page=page,
            per_page=per_page
        )

    def update_block(
        self,
        block_id: str,
        current_user_id: str,
        **kwargs
    ) -> PlannerBlock:
        """Update planner block fields with conflict re-check."""
        block = self.get_block(block_id, current_user_id)

        # Validate task if updated
        new_task_id = kwargs.get("task_id")
        if new_task_id is not None and new_task_id != block.task_id:
            task = self.task_repo.get_by_id(new_task_id)
            if not task:
                raise NotFoundException("Linked task not found")
            if task.user_id != current_user_id:
                raise BadRequestException("Linked task does not belong to the authenticated user")

        # Determine effective time range
        new_start = self._ensure_utc(kwargs.get("start_time")) if kwargs.get("start_time") else block.start_time
        new_end = self._ensure_utc(kwargs.get("end_time")) if kwargs.get("end_time") else block.end_time

        if new_start >= new_end:
            raise BadRequestException("start_time must be strictly earlier than end_time")

        new_status = kwargs.get("status") or block.status

        # Re-check conflict if time or status changed, excluding current block
        if new_status != "cancelled":
            conflict = self.planner_repo.check_conflict(
                user_id=current_user_id,
                start_time=new_start,
                end_time=new_end,
                exclude_block_id=block.id
            )
            if conflict:
                raise ConflictException(
                    f"Scheduling conflict with existing block '{conflict.title}' "
                    f"from {conflict.start_time.strftime('%H:%M')} to {conflict.end_time.strftime('%H:%M')}"
                )

        # Update normalized dates
        if "start_time" in kwargs and kwargs["start_time"]:
            kwargs["start_time"] = new_start
        if "end_time" in kwargs and kwargs["end_time"]:
            kwargs["end_time"] = new_end

        return self.planner_repo.update(block, **kwargs)

    def update_block_status(
        self,
        block_id: str,
        current_user_id: str,
        status: str
    ) -> PlannerBlock:
        """Update block status (scheduled, completed, cancelled, skipped)."""
        block = self.get_block(block_id, current_user_id)
        return self.planner_repo.update(block, status=status)

    def delete_block(self, block_id: str, current_user_id: str) -> None:
        """Delete a planner block ensuring caller owns the resource."""
        block = self.get_block(block_id, current_user_id)
        self.planner_repo.delete(block)

    def get_daily_summary(
        self,
        user_id: str,
        target_date_str: Optional[str] = None,
        utc_offset_hours: float = 0.0
    ) -> Dict[str, Any]:
        """
        Produce daily summary for user's calendar day window converted to UTC.
        """
        now_utc = datetime.now(timezone.utc)

        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise BadRequestException("Invalid date format. Expected YYYY-MM-DD")
        else:
            # Use local date based on user offset
            user_local_now = now_utc + timedelta(hours=utc_offset_hours)
            target_date = user_local_now.date()

        # Build local day start & end
        local_day_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        local_day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, 999999)

        # Convert local day boundaries to UTC
        day_start_utc = (local_day_start - timedelta(hours=utc_offset_hours)).replace(tzinfo=timezone.utc)
        day_end_utc = (local_day_end - timedelta(hours=utc_offset_hours)).replace(tzinfo=timezone.utc)

        return self.planner_repo.get_daily_summary(
            user_id=user_id,
            day_start=day_start_utc,
            day_end=day_end_utc,
            now_utc=now_utc
        )

    def _ensure_utc(self, dt: datetime) -> datetime:
        """Ensure datetime object is timezone-aware and converted to UTC."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

