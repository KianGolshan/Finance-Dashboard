import pytest
from app.ai.llm_extractor import _rule_based_extract
from app.ai.structured_output import validate_extraction, coerce_numeric


def test_rule_based_extraction():
    text = """
    Acme Corp Financial Statement FY 2024
    Revenue: $150,000,000
    EBITDA: $37,500,000
    Net Income: $22,000,000
    Total Debt: $45,000,000
    Cash and cash equivalents: $18,000,000
    """
    results = _rule_based_extract(text, "financial_statement")

    field_names = {r["field_name"] for r in results}
    assert "revenue" in field_names
    assert "ebitda" in field_names
    assert "net_income" in field_names
    assert "total_debt" in field_names
    assert "cash_and_equivalents" in field_names

    for r in results:
        assert r["confidence_score"] > 0
        assert r["extraction_method"] == "regex"


def test_rule_based_no_match():
    text = "This document contains no financial data."
    results = _rule_based_extract(text, None)
    assert len(results) == 0


def test_validate_extraction_financial():
    data = {
        "revenue": 150_000_000,
        "ebitda": 37_500_000,
        "net_income": 22_000_000,
        "currency": "USD",
    }
    validated, errors = validate_extraction("financial_statement", data)
    assert len(errors) == 0
    assert validated["revenue"] == 150_000_000


def test_coerce_numeric():
    assert coerce_numeric("150,000,000") == 150_000_000
    assert coerce_numeric("$50M") == 50_000_000
    assert coerce_numeric("2.5B") == 2_500_000_000
    assert coerce_numeric("500K") == 500_000
    assert coerce_numeric("(1,000)") == -1000.0
    assert coerce_numeric(None) is None
    assert coerce_numeric("abc") is None
    assert coerce_numeric(42) == 42.0
