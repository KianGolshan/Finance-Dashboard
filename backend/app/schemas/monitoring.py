
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.financial_metric import MetricType, MetricSource


class MetricCreate(BaseModel):
    company_id: str
    period_date: date
    metric_type: MetricType
    value: float
    currency: str = "USD"
    source: MetricSource = MetricSource.manual
    notes: str | None = None


class MetricResponse(BaseModel):
    id: str
    company_id: str
    period_date: date
    metric_type: MetricType
    value: float
    currency: str
    source: MetricSource
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MetricListResponse(BaseModel):
    metrics: list[MetricResponse]
    total: int


class MetricTimeSeries(BaseModel):
    metric_type: MetricType
    data_points: list[dict]


class PortfolioSummary(BaseModel):
    total_nav: float = 0.0
    total_invested: float = 0.0
    total_realized: float = 0.0
    unrealized_gain: float = 0.0
    gross_moic: float = 0.0
    fund_count: int = 0
    company_count: int = 0
    active_companies: int = 0
    sector_breakdown: list[dict] = Field(default_factory=list)
    geography_breakdown: list[dict] = Field(default_factory=list)
    vintage_breakdown: list[dict] = Field(default_factory=list)


class ScenarioCreate(BaseModel):
    company_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    assumptions: dict = Field(default_factory=dict)


class ScenarioResponse(BaseModel):
    id: str
    company_id: str
    name: str
    description: str | None
    assumptions: dict
    results: dict
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}
