"""Structured output validation for LLM extractions."""

from pydantic import BaseModel, Field, ValidationError
from typing import Any


class FinancialStatementOutput(BaseModel):
    revenue: float | None = None
    cost_of_goods_sold: float | None = None
    gross_profit: float | None = None
    ebitda: float | None = None
    net_income: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None
    total_equity: float | None = None
    cash_and_equivalents: float | None = None
    total_debt: float | None = None
    free_cash_flow: float | None = None
    period: str | None = None
    currency: str = "USD"


class InvestorReportOutput(BaseModel):
    nav: float | None = None
    distributions: float | None = None
    contributions: float | None = None
    irr: float | None = None
    moic: float | None = None
    dpi: float | None = None
    rvpi: float | None = None
    tvpi: float | None = None
    reporting_date: str | None = None


SCHEMA_MAP = {
    "financial_statement": FinancialStatementOutput,
    "investor_report": InvestorReportOutput,
}


def validate_extraction(document_type: str, extracted_data: dict) -> tuple[dict, list[str]]:
    """
    Validate extracted data against the schema for the document type.
    Returns (validated_data, list of validation errors).
    """
    schema_class = SCHEMA_MAP.get(document_type)
    if not schema_class:
        return extracted_data, []

    try:
        validated = schema_class(**extracted_data)
        return validated.model_dump(exclude_none=True), []
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        clean_data = {}
        for key, value in extracted_data.items():
            if hasattr(schema_class, key):
                try:
                    field_model = schema_class.model_validate({key: value})
                    clean_data[key] = getattr(field_model, key)
                except (ValidationError, Exception):
                    pass
        return clean_data, errors


def coerce_numeric(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("$", "").replace("(", "-").replace(")", "").strip()
        if cleaned.endswith(("M", "m")):
            cleaned = cleaned[:-1]
            multiplier = 1_000_000
        elif cleaned.endswith(("B", "b", "bn", "BN")):
            cleaned = cleaned.rstrip("BNbn")
            multiplier = 1_000_000_000
        elif cleaned.endswith(("K", "k")):
            cleaned = cleaned[:-1]
            multiplier = 1_000
        else:
            multiplier = 1
        try:
            return float(cleaned) * multiplier
        except ValueError:
            return None
    return None
