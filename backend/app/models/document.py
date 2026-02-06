import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class DocumentType(str, enum.Enum):
    financial_statement = "financial_statement"
    investor_report = "investor_report"
    valuation_memo = "valuation_memo"
    capital_call = "capital_call"
    distribution_notice = "distribution_notice"
    board_deck = "board_deck"
    due_diligence = "due_diligence"
    legal = "legal"
    other = "other"


class ProcessingStatus(str, enum.Enum):
    pending = "pending"
    parsing = "parsing"
    extracting = "extracting"
    validating = "validating"
    completed = "completed"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    document_type: Mapped[str | None] = mapped_column(SAEnum(DocumentType), nullable=True)
    processing_status: Mapped[str] = mapped_column(SAEnum(ProcessingStatus), default=ProcessingStatus.pending)
    extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="documents")
    extractions = relationship("Extraction", back_populates="document", lazy="selectin")
