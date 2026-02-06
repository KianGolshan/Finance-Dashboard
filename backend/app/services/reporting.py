import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportStatus
from app.models.audit_log import AuditLog
from app.schemas.report import ReportCreate


async def create_report(db: AsyncSession, data: ReportCreate) -> Report:
    report = Report(**data.model_dump())
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report


async def get_report(db: AsyncSession, report_id: str) -> Report | None:
    result = await db.execute(select(Report).where(Report.id == report_id))
    return result.scalar_one_or_none()


async def list_reports(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Report], int]:
    total = (await db.execute(select(func.count(Report.id)))).scalar()
    result = await db.execute(
        select(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total


async def update_report_status(
    db: AsyncSession,
    report_id: str,
    status: ReportStatus,
    output_path: str | None = None,
    error_message: str | None = None,
) -> Report | None:
    report = await get_report(db, report_id)
    if not report:
        return None
    report.status = status
    if output_path:
        report.output_path = output_path
    if error_message:
        report.error_message = error_message
    await db.flush()
    await db.refresh(report)
    return report


async def log_audit(
    db: AsyncSession,
    entity_type: str,
    entity_id: str,
    action: str,
    changes: dict,
    user_id: str = "system",
) -> AuditLog:
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes,
        user_id=user_id,
    )
    db.add(log)
    await db.flush()
    return log


async def get_audit_logs(
    db: AsyncSession,
    entity_type: str | None = None,
    entity_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
        count_query = count_query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
        count_query = count_query.where(AuditLog.entity_id == entity_id)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total
