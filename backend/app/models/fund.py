import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class FundStatus(str, enum.Enum):
    active = "active"
    closed = "closed"
    fundraising = "fundraising"


class FundStrategy(str, enum.Enum):
    buyout = "buyout"
    growth_equity = "growth_equity"
    venture_capital = "venture_capital"
    credit = "credit"
    real_assets = "real_assets"
    secondaries = "secondaries"


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    vintage_year: Mapped[int] = mapped_column(Integer, nullable=False)
    strategy: Mapped[str] = mapped_column(SAEnum(FundStrategy), nullable=False)
    aum: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(SAEnum(FundStatus), default=FundStatus.active)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    companies = relationship("Company", back_populates="fund", lazy="selectin")
