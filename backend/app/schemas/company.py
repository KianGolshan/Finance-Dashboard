from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.company import CompanyStatus, Sector


class CompanyCreate(BaseModel):
    fund_id: str
    name: str = Field(..., min_length=1, max_length=255)
    sector: Sector
    geography: str = Field(..., max_length=100)
    investment_date: date
    initial_investment: float = Field(..., gt=0)
    current_valuation: float = Field(..., ge=0)
    ownership_pct: float = Field(..., gt=0, le=100)
    currency: str = Field(default="USD", max_length=3)
    description: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    current_valuation: float | None = None
    ownership_pct: float | None = None
    status: CompanyStatus | None = None
    exit_date: date | None = None
    description: str | None = None


class CompanyResponse(BaseModel):
    id: str
    fund_id: str
    name: str
    sector: Sector
    geography: str
    investment_date: date
    exit_date: date | None
    initial_investment: float
    current_valuation: float
    ownership_pct: float
    currency: str
    status: CompanyStatus
    description: str | None
    moic: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyListResponse(BaseModel):
    companies: list[CompanyResponse]
    total: int
