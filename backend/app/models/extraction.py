import uuid
from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ExtractionMethod(str, enum.Enum):
    llm = "llm"
    regex = "regex"
    table_parse = "table_parse"
    manual = "manual"


class Extraction(Base):
    __tablename__ = "extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_value: Mapped[str] = mapped_column(String(2000), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), default="string")
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    extraction_method: Mapped[str] = mapped_column(SAEnum(ExtractionMethod), default=ExtractionMethod.llm)
    page_number: Mapped[int | None] = mapped_column(nullable=True)
    context_snippet: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="extractions")
