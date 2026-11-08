"""LifeOS - Automation Request Validation Schemas."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CreateAutomationRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=128)
    slug: Optional[str] = Field(None, max_length=64)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field("productivity", pattern="^(productivity|review|health|finance)$")
    trigger_type: str = Field("manual", pattern="^(manual|scheduled|event)$")
    cron_expression: Optional[str] = None
    scheduled_time: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    scheduled_days: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class UpdateAutomationRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=128)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, pattern="^(productivity|review|health|finance)$")
    trigger_type: Optional[str] = Field(None, pattern="^(manual|scheduled|event)$")
    cron_expression: Optional[str] = None
    scheduled_time: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    scheduled_days: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None


class ExecuteAutomationRequest(BaseModel):
    user_request: Optional[str] = Field(None, max_length=1000)
    idempotency_key: Optional[str] = Field(None, max_length=128)


class RejectApprovalRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=255)
