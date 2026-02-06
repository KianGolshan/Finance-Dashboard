import pytest
from app.services.valuation_engine import run_dcf, run_comps, run_sensitivity
from app.schemas.valuation import DCFInputs, CompsInputs, SensitivityInputs


def test_dcf_basic():
    inputs = DCFInputs(
        base_revenue=100_000_000,
        projection_years=5,
        revenue_growth_rates=[0.10, 0.10, 0.08, 0.08, 0.06],
        ebitda_margins=[0.25, 0.26, 0.27, 0.28, 0.28],
        discount_rate=0.10,
        terminal_growth_rate=0.025,
        tax_rate=0.25,
        capex_pct_revenue=0.05,
        nwc_pct_revenue=0.10,
        net_debt=20_000_000,
    )
    result = run_dcf(inputs)

    assert "projections" in result
    assert len(result["projections"]) == 5
    assert result["enterprise_value"] > 0
    assert result["equity_value"] > 0
    assert result["equity_value"] == result["enterprise_value"] - 20_000_000

    # Revenue should grow
    revenues = [p["revenue"] for p in result["projections"]]
    for i in range(1, len(revenues)):
        assert revenues[i] > revenues[i - 1]

    # All PV(FCF) values should be positive
    pv_fcfs = [p["pv_fcf"] for p in result["projections"]]
    assert all(pv > 0 for pv in pv_fcfs)


def test_dcf_zero_revenue():
    inputs = DCFInputs(base_revenue=0, projection_years=3)
    result = run_dcf(inputs)
    assert result["enterprise_value"] == 0.0


def test_comps():
    inputs = CompsInputs(
        comparable_companies=[
            {"name": "Comp A", "enterprise_value": 500_000_000, "ebitda": 50_000_000},
            {"name": "Comp B", "enterprise_value": 800_000_000, "ebitda": 100_000_000},
            {"name": "Comp C", "enterprise_value": 600_000_000, "ebitda": 60_000_000},
        ],
        metric="ebitda",
        target_metric_value=75_000_000,
    )
    result = run_comps(inputs)

    assert "comparables" in result
    assert len(result["comparables"]) == 3
    assert result["mean_multiple"] > 0
    assert result["median_multiple"] > 0
    assert result["implied_enterprise_value"] > 0
    assert result["min_multiple"] <= result["median_multiple"] <= result["max_multiple"]


def test_comps_empty():
    inputs = CompsInputs(comparable_companies=[], metric="ebitda")
    result = run_comps(inputs)
    assert "error" in result


def test_sensitivity():
    result = run_sensitivity(
        base_ev=500_000_000,
        inputs=SensitivityInputs(
            variable_1="discount_rate",
            variable_1_range=[0.08, 0.09, 0.10, 0.11, 0.12],
            variable_2="terminal_growth_rate",
            variable_2_range=[0.015, 0.02, 0.025, 0.03, 0.035],
        ),
    )

    assert "matrix" in result
    assert len(result["matrix"]) == 5
    assert len(result["matrix"][0]) == 5
    assert result["base_enterprise_value"] == 500_000_000

    # Higher discount rate should lower EV (first row entry > last row entry for same column)
    assert result["matrix"][0][2] > result["matrix"][-1][2]
