from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str
    user_id: str
    title: str
    body: str
    notification_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    data_payload: Optional[str] = None
    dedup_hash: Optional[str] = None
    is_delivered: bool = False
    delivered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NotificationPreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str
    user_id: str
    tasks_enabled: bool
    planner_enabled: bool
    habits_enabled: bool
    goals_enabled: bool
    finance_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    timezone: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UpdateNotificationPreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks_enabled: Optional[bool] = None
    planner_enabled: Optional[bool] = None
    habits_enabled: Optional[bool] = None
    goals_enabled: Optional[bool] = None
    finance_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

    @field_validator("quiet_hours_start", "quiet_hours_end")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", v):
                raise ValueError("Time must be in 24-hour 'HH:MM' format.")
        return v


class CreateReminderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_time: datetime
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[str] = Field(None, max_length=36)
    is_recurring: bool = False
    recurrence_rule: Optional[str] = Field(None, max_length=50)

    @field_validator("recurrence_rule")
    @classmethod
    def validate_recurrence(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_rules = {"daily", "weekdays", "weekly", "monthly"}
            if v.lower() not in valid_rules:
                raise ValueError(f"Recurrence rule must be one of: {', '.join(sorted(valid_rules))}")
            return v.lower()
        return v


class UpdateReminderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_time: Optional[datetime] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_statuses = {"pending", "triggered", "cancelled", "snoozed", "expired"}
            if v.lower() not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(sorted(valid_statuses))}")
            return v.lower()
        return v

    @field_validator("recurrence_rule")
    @classmethod
    def validate_recurrence(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_rules = {"daily", "weekdays", "weekly", "monthly"}
            if v.lower() not in valid_rules:
                raise ValueError(f"Recurrence rule must be one of: {', '.join(sorted(valid_rules))}")
            return v.lower()
        return v


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    reminder_time: datetime
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    is_recurring: bool
    recurrence_rule: Optional[str] = None
    status: str
    triggered_at: Optional[datetime] = None
    notification_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RegisterDeviceTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., min_length=1, max_length=255)
    device_type: str = Field("mobile", max_length=20)
    device_name: Optional[str] = Field(None, max_length=100)

