import uuid
from datetime import date, datetime

from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class CompanyStatus(str, enum.Enum):
    active = "active"
    exited = "exited"
    written_off = "written_off"
    marked_up = "marked_up"


class Sector(str, enum.Enum):
    technology = "technology"
    healthcare = "healthcare"
    financials = "financials"
    industrials = "industrials"
    consumer = "consumer"
    energy = "energy"
    real_estate = "real_estate"
    materials = "materials"
    telecom = "telecom"
    utilities = "utilities"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_id: Mapped[str] = mapped_column(String(36), ForeignKey("funds.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(SAEnum(Sector), nullable=False)
    geography: Mapped[str] = mapped_column(String(100), nullable=False)
    investment_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    initial_investment: Mapped[float] = mapped_column(Float, nullable=False)
    current_valuation: Mapped[float] = mapped_column(Float, nullable=False)
    ownership_pct: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(SAEnum(CompanyStatus), default=CompanyStatus.active)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fund = relationship("Fund", back_populates="companies")
    financial_metrics = relationship("FinancialMetric", back_populates="company", lazy="selectin")
    documents = relationship("Document", back_populates="company", lazy="selectin")
    valuations = relationship("Valuation", back_populates="company", lazy="selectin")
    scenarios = relationship("Scenario", back_populates="company", lazy="selectin")
