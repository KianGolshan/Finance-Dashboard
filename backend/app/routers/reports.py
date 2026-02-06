import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
    AuditLogResponse,
    AuditLogListResponse,
)
from app.services import reporting as svc

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(data: ReportCreate, db: AsyncSession = Depends(get_db)):
    report = await svc.create_report(db, data)
    return ReportResponse.model_validate(report)


@router.get("", response_model=ReportListResponse)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    reports, total = await svc.list_reports(db, skip, limit)
    return ReportListResponse(
        reports=[ReportResponse.model_validate(r) for r in reports],
        total=total,
    )


@router.get("/audit-log", response_model=AuditLogListResponse)
async def get_audit_logs(
    entity_type: str | None = None,
    entity_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await svc.get_audit_logs(db, entity_type, entity_id, skip, limit)
    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(l) for l in logs],
        total=total,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await svc.get_report(db, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return ReportResponse.model_validate(report)
