
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.valuation import ValuationMethod, ValuationStatus


class DCFInputs(BaseModel):
    projection_years: int = Field(default=5, ge=1, le=10)
    revenue_growth_rates: list[float] = Field(default_factory=list)
    ebitda_margins: list[float] = Field(default_factory=list)
    discount_rate: float = Field(default=0.10, ge=0.01, le=0.50)
    terminal_growth_rate: float = Field(default=0.025, ge=0.0, le=0.10)
    tax_rate: float = Field(default=0.25, ge=0.0, le=0.50)
    capex_pct_revenue: float = Field(default=0.05, ge=0.0, le=0.50)
    nwc_pct_revenue: float = Field(default=0.10, ge=0.0, le=0.50)
    base_revenue: float | None = None
    base_ebitda: float | None = None
    net_debt: float = 0.0


class CompsInputs(BaseModel):
    comparable_companies: list[dict] = Field(default_factory=list)
    metric: str = "ebitda"
    target_metric_value: float | None = None
    selected_multiple: float | None = None


class SensitivityInputs(BaseModel):
    base_valuation_id: str | None = None
    variable_1: str = "discount_rate"
    variable_1_range: list[float] = Field(default_factory=list)
    variable_2: str = "terminal_growth_rate"
    variable_2_range: list[float] = Field(default_factory=list)


class ValuationCreate(BaseModel):
    company_id: str
    valuation_date: date
    method: ValuationMethod
    inputs: dict = Field(default_factory=dict)
    notes: str | None = None


class ValuationResponse(BaseModel):
    id: str
    company_id: str
    valuation_date: date
    method: ValuationMethod
    inputs: dict
    outputs: dict
    enterprise_value: float | None
    equity_value: float | None
    implied_multiple: float | None
    currency: str
    status: ValuationStatus
    notes: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ValuationListResponse(BaseModel):
    valuations: list[ValuationResponse]
    total: int


class OverrideCreate(BaseModel):
    field_name: str
    original_value: float
    override_value: float
    reason: str
    created_by: str


class OverrideResponse(BaseModel):
    id: str
    valuation_id: str
    field_name: str
    original_value: float
    override_value: float
    reason: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}
