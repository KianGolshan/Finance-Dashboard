import uuid
from datetime import date, datetime

from sqlalchemy import String, Float, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class MetricType(str, enum.Enum):
    revenue = "revenue"
    ebitda = "ebitda"
    net_income = "net_income"
    gross_profit = "gross_profit"
    free_cash_flow = "free_cash_flow"
    total_debt = "total_debt"
    cash = "cash"
    enterprise_value = "enterprise_value"
    equity_value = "equity_value"
    revenue_growth = "revenue_growth"
    ebitda_margin = "ebitda_margin"
    net_debt = "net_debt"
    capex = "capex"
    working_capital = "working_capital"
    employees = "employees"
    arr = "arr"
    mrr = "mrr"
    customer_count = "customer_count"
    churn_rate = "churn_rate"
    ltv = "ltv"
    cac = "cac"


class MetricSource(str, enum.Enum):
    reported = "reported"
    extracted = "extracted"
    calculated = "calculated"
    estimated = "estimated"
    manual = "manual"


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    period_date: Mapped[date] = mapped_column(Date, nullable=False)
    metric_type: Mapped[str] = mapped_column(SAEnum(MetricType), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    source: Mapped[str] = mapped_column(SAEnum(MetricSource), default=MetricSource.manual)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="financial_metrics")
