import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.valuation import Valuation, ValuationOverride, ValuationMethod
from app.models.financial_metric import FinancialMetric, MetricType
from app.schemas.valuation import (
    ValuationCreate,
    DCFInputs,
    CompsInputs,
    SensitivityInputs,
    OverrideCreate,
)


async def get_latest_metrics(db: AsyncSession, company_id: str) -> dict[str, float]:
    result = await db.execute(
        select(FinancialMetric)
        .where(FinancialMetric.company_id == company_id)
        .order_by(FinancialMetric.period_date.desc())
    )
    metrics = list(result.scalars().all())

    latest: dict[str, float] = {}
    seen: set[str] = set()
    for m in metrics:
        if m.metric_type not in seen:
            latest[m.metric_type] = m.value
            seen.add(m.metric_type)
    return latest


def run_dcf(inputs: DCFInputs) -> dict:
    base_revenue = inputs.base_revenue or 0.0
    projection_years = inputs.projection_years
    discount_rate = inputs.discount_rate
    terminal_growth = inputs.terminal_growth_rate
    tax_rate = inputs.tax_rate

    growth_rates = inputs.revenue_growth_rates or [0.10] * projection_years
    margins = inputs.ebitda_margins or [0.25] * projection_years

    if len(growth_rates) < projection_years:
        growth_rates.extend([growth_rates[-1]] * (projection_years - len(growth_rates)))
    if len(margins) < projection_years:
        margins.extend([margins[-1]] * (projection_years - len(margins)))

    projections = []
    revenue = base_revenue
    total_pv_fcf = 0.0

    for year in range(1, projection_years + 1):
        revenue *= (1 + growth_rates[year - 1])
        ebitda = revenue * margins[year - 1]
        tax = ebitda * tax_rate
        capex = revenue * inputs.capex_pct_revenue
        nwc_change = revenue * inputs.nwc_pct_revenue * growth_rates[year - 1]
        fcf = ebitda - tax - capex - nwc_change
        discount_factor = (1 + discount_rate) ** year
        pv_fcf = fcf / discount_factor
        total_pv_fcf += pv_fcf

        projections.append({
            "year": year,
            "revenue": round(revenue, 2),
            "ebitda": round(ebitda, 2),
            "ebitda_margin": round(margins[year - 1], 4),
            "fcf": round(fcf, 2),
            "pv_fcf": round(pv_fcf, 2),
            "discount_factor": round(discount_factor, 4),
        })

    terminal_fcf = projections[-1]["fcf"] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)

    enterprise_value = total_pv_fcf + pv_terminal
    equity_value = enterprise_value - inputs.net_debt

    return {
        "projections": projections,
        "terminal_value": round(terminal_value, 2),
        "pv_terminal_value": round(pv_terminal, 2),
        "pv_fcf_total": round(total_pv_fcf, 2),
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "implied_ev_ebitda": round(enterprise_value / projections[0]["ebitda"], 2) if projections[0]["ebitda"] else None,
    }


def run_comps(inputs: CompsInputs) -> dict:
    if not inputs.comparable_companies:
        return {"error": "No comparable companies provided"}

    multiples = []
    for comp in inputs.comparable_companies:
        name = comp.get("name", "Unknown")
        ev = comp.get("enterprise_value", 0)
        metric_val = comp.get(inputs.metric, 0)
        if metric_val and metric_val > 0:
            multiple = ev / metric_val
            multiples.append({"name": name, "multiple": round(multiple, 2), "ev": ev, inputs.metric: metric_val})

    if not multiples:
        return {"error": "Could not compute multiples"}

    mult_values = [m["multiple"] for m in multiples]
    mean_multiple = sum(mult_values) / len(mult_values)
    sorted_mults = sorted(mult_values)
    median_multiple = sorted_mults[len(sorted_mults) // 2]

    selected = inputs.selected_multiple or median_multiple
    target_value = inputs.target_metric_value or 0
    implied_ev = selected * target_value

    return {
        "comparables": multiples,
        "mean_multiple": round(mean_multiple, 2),
        "median_multiple": round(median_multiple, 2),
        "min_multiple": round(min(mult_values), 2),
        "max_multiple": round(max(mult_values), 2),
        "selected_multiple": round(selected, 2),
        "target_metric": inputs.metric,
        "target_metric_value": target_value,
        "implied_enterprise_value": round(implied_ev, 2),
    }


def run_sensitivity(base_ev: float, inputs: SensitivityInputs) -> dict:
    var1_range = inputs.variable_1_range or [0.08, 0.09, 0.10, 0.11, 0.12]
    var2_range = inputs.variable_2_range or [0.015, 0.02, 0.025, 0.03, 0.035]

    matrix = []
    for v1 in var1_range:
        row = []
        for v2 in var2_range:
            factor1 = 0.10 / v1 if v1 > 0 else 1.0
            factor2 = v2 / 0.025 if inputs.variable_2 == "terminal_growth_rate" else 1.0
            adjusted_ev = base_ev * factor1 * factor2
            row.append(round(adjusted_ev, 2))
        matrix.append(row)

    return {
        "variable_1": inputs.variable_1,
        "variable_1_range": var1_range,
        "variable_2": inputs.variable_2,
        "variable_2_range": var2_range,
        "matrix": matrix,
        "base_enterprise_value": base_ev,
    }


async def create_valuation(db: AsyncSession, data: ValuationCreate) -> Valuation:
    outputs = {}
    ev = None
    eq_val = None
    implied_mult = None

    if data.method == ValuationMethod.dcf:
        dcf_inputs = DCFInputs(**data.inputs)
        metrics = await get_latest_metrics(db, data.company_id)
        if dcf_inputs.base_revenue is None and MetricType.revenue in metrics:
            dcf_inputs.base_revenue = metrics[MetricType.revenue]
        if dcf_inputs.base_ebitda is None and MetricType.ebitda in metrics:
            dcf_inputs.base_ebitda = metrics[MetricType.ebitda]
        outputs = run_dcf(dcf_inputs)
        ev = outputs.get("enterprise_value")
        eq_val = outputs.get("equity_value")
        implied_mult = outputs.get("implied_ev_ebitda")

    elif data.method == ValuationMethod.comparable_companies:
        comps_inputs = CompsInputs(**data.inputs)
        outputs = run_comps(comps_inputs)
        ev = outputs.get("implied_enterprise_value")

    elif data.method == ValuationMethod.sensitivity:
        sens_inputs = SensitivityInputs(**data.inputs)
        base_ev = data.inputs.get("base_enterprise_value", 0)
        outputs = run_sensitivity(base_ev, sens_inputs)

    valuation = Valuation(
        company_id=data.company_id,
        valuation_date=data.valuation_date,
        method=data.method,
        inputs=data.inputs,
        outputs=outputs,
        enterprise_value=ev,
        equity_value=eq_val,
        implied_multiple=implied_mult,
        notes=data.notes,
    )
    db.add(valuation)
    await db.flush()
    await db.refresh(valuation)
    return valuation


async def get_valuation(db: AsyncSession, valuation_id: str) -> Valuation | None:
    result = await db.execute(select(Valuation).where(Valuation.id == valuation_id))
    return result.scalar_one_or_none()


async def list_valuations(
    db: AsyncSession,
    company_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Valuation], int]:
    from sqlalchemy import func

    query = select(Valuation)
    count_query = select(func.count(Valuation.id))

    if company_id:
        query = query.where(Valuation.company_id == company_id)
        count_query = count_query.where(Valuation.company_id == company_id)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(query.order_by(Valuation.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def add_override(db: AsyncSession, valuation_id: str, data: OverrideCreate) -> ValuationOverride:
    override = ValuationOverride(valuation_id=valuation_id, **data.model_dump())
    db.add(override)
    await db.flush()
    await db.refresh(override)
    return override
