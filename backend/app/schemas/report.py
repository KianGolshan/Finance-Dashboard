
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.report import ReportType, ReportStatus


class ReportCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    report_type: ReportType
    entity_id: str | None = None
    entity_type: str | None = None
    parameters: dict = Field(default_factory=dict)
    output_format: str = "pdf"


class ReportResponse(BaseModel):
    id: str
    name: str
    report_type: ReportType
    entity_id: str | None
    entity_type: str | None
    parameters: dict
    output_path: str | None
    output_format: str
    status: ReportStatus
    error_message: str | None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    reports: list[ReportResponse]
    total: int


class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    changes: dict
    user_id: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int
