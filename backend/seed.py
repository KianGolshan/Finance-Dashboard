"""Seed the database with sample data for development."""
import asyncio
import uuid
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_engine, get_session_factory, Base
from app.models.fund import Fund, FundStrategy, FundStatus
from app.models.company import Company, Sector, CompanyStatus
from app.models.financial_metric import FinancialMetric, MetricType, MetricSource


async def seed():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = get_session_factory()
    async with session_factory() as db:
        # Fund 1: Growth Equity
        fund1_id = str(uuid.uuid4())
        fund1 = Fund(
            id=fund1_id, name="Meridian Growth Partners III", vintage_year=2022,
            strategy=FundStrategy.growth_equity, aum=750_000_000, currency="USD",
            status=FundStatus.active, description="Mid-market growth equity fund targeting technology and healthcare.",
        )

        # Fund 2: Buyout
        fund2_id = str(uuid.uuid4())
        fund2 = Fund(
            id=fund2_id, name="Meridian Capital Buyout Fund V", vintage_year=2023,
            strategy=FundStrategy.buyout, aum=1_200_000_000, currency="USD",
            status=FundStatus.active, description="Large-cap buyout fund focused on industrials and technology.",
        )

        db.add_all([fund1, fund2])

        # Companies
        companies_data = [
            (fund1_id, "NovaTech Solutions", Sector.technology, "North America", date(2022, 3, 15), 45_000_000, 112_000_000, 28.5),
            (fund1_id, "MedVance Health", Sector.healthcare, "North America", date(2022, 7, 1), 35_000_000, 58_000_000, 22.0),
            (fund1_id, "CloudScale Analytics", Sector.technology, "Europe", date(2022, 11, 20), 60_000_000, 142_000_000, 35.0),
            (fund1_id, "GreenEdge Energy", Sector.energy, "North America", date(2023, 2, 10), 25_000_000, 31_000_000, 15.0),
            (fund2_id, "Precision Manufacturing Co", Sector.industrials, "North America", date(2023, 5, 1), 120_000_000, 185_000_000, 65.0),
            (fund2_id, "DataFort Security", Sector.technology, "North America", date(2023, 9, 15), 85_000_000, 130_000_000, 45.0),
            (fund2_id, "Apex Consumer Brands", Sector.consumer, "Europe", date(2024, 1, 10), 95_000_000, 102_000_000, 55.0),
        ]

        company_ids = []
        for fund_id, name, sector, geo, inv_date, cost, val, own in companies_data:
            cid = str(uuid.uuid4())
            company_ids.append(cid)
            db.add(Company(
                id=cid, fund_id=fund_id, name=name, sector=sector, geography=geo,
                investment_date=inv_date, initial_investment=cost, current_valuation=val,
                ownership_pct=own, status=CompanyStatus.active,
            ))

        # Financial metrics for first 3 companies
        metric_data = [
            # NovaTech
            (company_ids[0], date(2023, 3, 31), MetricType.revenue, 80_000_000),
            (company_ids[0], date(2023, 6, 30), MetricType.revenue, 88_000_000),
            (company_ids[0], date(2023, 9, 30), MetricType.revenue, 95_000_000),
            (company_ids[0], date(2023, 12, 31), MetricType.revenue, 105_000_000),
            (company_ids[0], date(2024, 3, 31), MetricType.revenue, 115_000_000),
            (company_ids[0], date(2023, 12, 31), MetricType.ebitda, 26_000_000),
            (company_ids[0], date(2024, 3, 31), MetricType.ebitda, 30_000_000),
            (company_ids[0], date(2024, 3, 31), MetricType.arr, 120_000_000),
            (company_ids[0], date(2024, 3, 31), MetricType.net_income, 18_000_000),
            # MedVance
            (company_ids[1], date(2023, 12, 31), MetricType.revenue, 52_000_000),
            (company_ids[1], date(2024, 3, 31), MetricType.revenue, 58_000_000),
            (company_ids[1], date(2024, 3, 31), MetricType.ebitda, 12_000_000),
            # CloudScale
            (company_ids[2], date(2023, 12, 31), MetricType.revenue, 130_000_000),
            (company_ids[2], date(2024, 3, 31), MetricType.revenue, 148_000_000),
            (company_ids[2], date(2024, 3, 31), MetricType.ebitda, 42_000_000),
            (company_ids[2], date(2024, 3, 31), MetricType.arr, 155_000_000),
        ]

        for cid, pdate, mtype, val in metric_data:
            db.add(FinancialMetric(
                company_id=cid, period_date=pdate, metric_type=mtype,
                value=val, source=MetricSource.reported,
            ))

        await db.commit()
        print(f"Seeded {len(companies_data)} companies across 2 funds with {len(metric_data)} metrics.")


if __name__ == "__main__":
    asyncio.run(seed())
