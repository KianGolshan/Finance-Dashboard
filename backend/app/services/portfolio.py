import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fund import Fund
from app.models.company import Company, CompanyStatus
from app.schemas.fund import FundCreate, FundUpdate
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.monitoring import PortfolioSummary


async def create_fund(db: AsyncSession, data: FundCreate) -> Fund:
    fund = Fund(**data.model_dump())
    db.add(fund)
    await db.flush()
    await db.refresh(fund)
    return fund


async def get_fund(db: AsyncSession, fund_id: str) -> Fund | None:
    result = await db.execute(select(Fund).where(Fund.id == fund_id))
    return result.scalar_one_or_none()


async def list_funds(db: AsyncSession, skip: int = 0, limit: int = 50) -> tuple[list[Fund], int]:
    count_result = await db.execute(select(func.count(Fund.id)))
    total = count_result.scalar()

    result = await db.execute(
        select(Fund).order_by(Fund.created_at.desc()).offset(skip).limit(limit)
    )
    funds = list(result.scalars().all())
    return funds, total


async def update_fund(db: AsyncSession, fund_id: str, data: FundUpdate) -> Fund | None:
    fund = await get_fund(db, fund_id)
    if not fund:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(fund, field, value)
    await db.flush()
    await db.refresh(fund)
    return fund


async def delete_fund(db: AsyncSession, fund_id: str) -> bool:
    fund = await get_fund(db, fund_id)
    if not fund:
        return False
    await db.delete(fund)
    return True


async def create_company(db: AsyncSession, data: CompanyCreate) -> Company:
    company = Company(**data.model_dump())
    db.add(company)
    await db.flush()
    await db.refresh(company)
    return company


async def get_company(db: AsyncSession, company_id: str) -> Company | None:
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalar_one_or_none()


async def list_companies(
    db: AsyncSession,
    fund_id: str | None = None,
    status: CompanyStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Company], int]:
    query = select(Company)
    count_query = select(func.count(Company.id))

    if fund_id:
        query = query.where(Company.fund_id == fund_id)
        count_query = count_query.where(Company.fund_id == fund_id)
    if status:
        query = query.where(Company.status == status)
        count_query = count_query.where(Company.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    result = await db.execute(
        query.order_by(Company.created_at.desc()).offset(skip).limit(limit)
    )
    companies = list(result.scalars().all())
    return companies, total


async def update_company(db: AsyncSession, company_id: str, data: CompanyUpdate) -> Company | None:
    company = await get_company(db, company_id)
    if not company:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.flush()
    await db.refresh(company)
    return company


async def get_portfolio_summary(db: AsyncSession) -> PortfolioSummary:
    companies_result = await db.execute(select(Company))
    companies = list(companies_result.scalars().all())

    funds_result = await db.execute(select(func.count(Fund.id)))
    fund_count = funds_result.scalar()

    total_invested = sum(c.initial_investment for c in companies)
    total_nav = sum(c.current_valuation for c in companies if c.status == CompanyStatus.active)
    active = [c for c in companies if c.status == CompanyStatus.active]

    sector_counts: dict[str, dict] = {}
    geo_counts: dict[str, dict] = {}
    for c in companies:
        sector = c.sector
        if sector not in sector_counts:
            sector_counts[sector] = {"sector": sector, "count": 0, "value": 0.0}
        sector_counts[sector]["count"] += 1
        sector_counts[sector]["value"] += c.current_valuation

        geo = c.geography
        if geo not in geo_counts:
            geo_counts[geo] = {"geography": geo, "count": 0, "value": 0.0}
        geo_counts[geo]["count"] += 1
        geo_counts[geo]["value"] += c.current_valuation

    return PortfolioSummary(
        total_nav=total_nav,
        total_invested=total_invested,
        total_realized=0.0,
        unrealized_gain=total_nav - total_invested,
        gross_moic=total_nav / total_invested if total_invested > 0 else 0.0,
        fund_count=fund_count,
        company_count=len(companies),
        active_companies=len(active),
        sector_breakdown=list(sector_counts.values()),
        geography_breakdown=list(geo_counts.values()),
    )
