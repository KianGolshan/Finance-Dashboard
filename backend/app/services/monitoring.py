import uuid
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_metric import FinancialMetric, MetricType
from app.models.scenario import Scenario
from app.schemas.monitoring import MetricCreate, ScenarioCreate


async def create_metric(db: AsyncSession, data: MetricCreate) -> FinancialMetric:
    metric = FinancialMetric(**data.model_dump())
    db.add(metric)
    await db.flush()
    await db.refresh(metric)
    return metric


async def list_metrics(
    db: AsyncSession,
    company_id: str,
    metric_type: MetricType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[FinancialMetric], int]:
    query = select(FinancialMetric).where(FinancialMetric.company_id == company_id)
    count_query = select(func.count(FinancialMetric.id)).where(FinancialMetric.company_id == company_id)

    if metric_type:
        query = query.where(FinancialMetric.metric_type == metric_type)
        count_query = count_query.where(FinancialMetric.metric_type == metric_type)
    if start_date:
        query = query.where(FinancialMetric.period_date >= start_date)
        count_query = count_query.where(FinancialMetric.period_date >= start_date)
    if end_date:
        query = query.where(FinancialMetric.period_date <= end_date)
        count_query = count_query.where(FinancialMetric.period_date <= end_date)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(FinancialMetric.period_date.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total


async def get_time_series(
    db: AsyncSession,
    company_id: str,
    metric_type: MetricType,
) -> list[dict]:
    result = await db.execute(
        select(FinancialMetric)
        .where(FinancialMetric.company_id == company_id, FinancialMetric.metric_type == metric_type)
        .order_by(FinancialMetric.period_date.asc())
    )
    metrics = list(result.scalars().all())
    return [
        {"date": m.period_date.isoformat(), "value": m.value, "source": m.source}
        for m in metrics
    ]


async def create_scenario(db: AsyncSession, data: ScenarioCreate) -> Scenario:
    assumptions = data.assumptions
    results = _compute_scenario(assumptions)

    scenario = Scenario(
        company_id=data.company_id,
        name=data.name,
        description=data.description,
        assumptions=assumptions,
        results=results,
    )
    db.add(scenario)
    await db.flush()
    await db.refresh(scenario)
    return scenario


def _compute_scenario(assumptions: dict) -> dict:
    base_revenue = assumptions.get("base_revenue", 0)
    growth_rate = assumptions.get("revenue_growth", 0.1)
    margin = assumptions.get("ebitda_margin", 0.25)
    years = assumptions.get("projection_years", 5)
    exit_multiple = assumptions.get("exit_multiple", 10)
    initial_investment = assumptions.get("initial_investment", 0)
    ownership = assumptions.get("ownership_pct", 1.0)

    projections = []
    revenue = base_revenue
    for year in range(1, years + 1):
        revenue *= (1 + growth_rate)
        ebitda = revenue * margin
        projections.append({
            "year": year,
            "revenue": round(revenue, 2),
            "ebitda": round(ebitda, 2),
        })

    exit_ebitda = projections[-1]["ebitda"] if projections else 0
    exit_ev = exit_ebitda * exit_multiple
    equity_proceeds = exit_ev * ownership
    moic = equity_proceeds / initial_investment if initial_investment > 0 else 0
    irr = (moic ** (1 / years) - 1) if moic > 0 and years > 0 else 0

    return {
        "projections": projections,
        "exit_ebitda": round(exit_ebitda, 2),
        "exit_enterprise_value": round(exit_ev, 2),
        "equity_proceeds": round(equity_proceeds, 2),
        "moic": round(moic, 2),
        "irr": round(irr, 4),
    }


async def list_scenarios(
    db: AsyncSession,
    company_id: str,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Scenario], int]:
    count_result = await db.execute(
        select(func.count(Scenario.id)).where(Scenario.company_id == company_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Scenario)
        .where(Scenario.company_id == company_id)
        .order_by(Scenario.created_at.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total
