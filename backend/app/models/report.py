import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base


class ReportType(str, enum.Enum):
    portfolio_summary = "portfolio_summary"
    company_tearsheet = "company_tearsheet"
    valuation_report = "valuation_report"
    quarterly_review = "quarterly_review"
    custom = "custom"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    generating = "generating"
    completed = "completed"
    failed = "failed"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(SAEnum(ReportType), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_format: Mapped[str] = mapped_column(String(10), default="pdf")
    status: Mapped[str] = mapped_column(SAEnum(ReportStatus), default=ReportStatus.pending)
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
