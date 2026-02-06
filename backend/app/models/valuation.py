import uuid
from datetime import date, datetime

from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ValuationMethod(str, enum.Enum):
    dcf = "dcf"
    comparable_companies = "comparable_companies"
    comparable_transactions = "comparable_transactions"
    sensitivity = "sensitivity"
    weighted_blend = "weighted_blend"


class ValuationStatus(str, enum.Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"
    superseded = "superseded"


class Valuation(Base):
    __tablename__ = "valuations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    valuation_date: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[str] = mapped_column(SAEnum(ValuationMethod), nullable=False)
    inputs: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    outputs: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    enterprise_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    equity_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    implied_multiple: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(SAEnum(ValuationStatus), default=ValuationStatus.draft)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="valuations")
    overrides = relationship("ValuationOverride", back_populates="valuation", lazy="selectin")


class ValuationOverride(Base):
    __tablename__ = "valuation_overrides"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    valuation_id: Mapped[str] = mapped_column(String(36), ForeignKey("valuations.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_value: Mapped[float] = mapped_column(Float, nullable=False)
    override_value: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    valuation = relationship("Valuation", back_populates="overrides")
