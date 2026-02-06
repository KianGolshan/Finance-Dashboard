from datetime import datetime
from pydantic import BaseModel, Field

from app.models.fund import FundStatus, FundStrategy


class FundCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    vintage_year: int = Field(..., ge=1990, le=2030)
    strategy: FundStrategy
    aum: float | None = None
    currency: str = Field(default="USD", max_length=3)
    description: str | None = None


class FundUpdate(BaseModel):
    name: str | None = None
    aum: float | None = None
    status: FundStatus | None = None
    description: str | None = None


class FundResponse(BaseModel):
    id: str
    name: str
    vintage_year: int
    strategy: FundStrategy
    aum: float | None
    currency: str
    status: FundStatus
    description: str | None
    created_at: datetime
    updated_at: datetime
    company_count: int = 0
    total_invested: float = 0.0
    total_value: float = 0.0

    model_config = {"from_attributes": True}


class FundListResponse(BaseModel):
    funds: list[FundResponse]
    total: int
