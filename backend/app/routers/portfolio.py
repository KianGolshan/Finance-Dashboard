import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.company import CompanyStatus
from app.schemas.fund import FundCreate, FundUpdate, FundResponse, FundListResponse
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
from app.schemas.monitoring import PortfolioSummary
from app.services import portfolio as svc

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: AsyncSession = Depends(get_db)):
    return await svc.get_portfolio_summary(db)


# --- Funds ---

@router.post("/funds", response_model=FundResponse, status_code=201)
async def create_fund(data: FundCreate, db: AsyncSession = Depends(get_db)):
    fund = await svc.create_fund(db, data)
    return _fund_response(fund)


@router.get("/funds", response_model=FundListResponse)
async def list_funds(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    funds, total = await svc.list_funds(db, skip, limit)
    return FundListResponse(
        funds=[_fund_response(f) for f in funds],
        total=total,
    )


@router.get("/funds/{fund_id}", response_model=FundResponse)
async def get_fund(fund_id: str, db: AsyncSession = Depends(get_db)):
    fund = await svc.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(404, "Fund not found")
    return _fund_response(fund)


@router.patch("/funds/{fund_id}", response_model=FundResponse)
async def update_fund(fund_id: str, data: FundUpdate, db: AsyncSession = Depends(get_db)):
    fund = await svc.update_fund(db, fund_id, data)
    if not fund:
        raise HTTPException(404, "Fund not found")
    return _fund_response(fund)


@router.delete("/funds/{fund_id}", status_code=204)
async def delete_fund(fund_id: str, db: AsyncSession = Depends(get_db)):
    if not await svc.delete_fund(db, fund_id):
        raise HTTPException(404, "Fund not found")


# --- Companies ---

@router.post("/companies", response_model=CompanyResponse, status_code=201)
async def create_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    company = await svc.create_company(db, data)
    return _company_response(company)


@router.get("/companies", response_model=CompanyListResponse)
async def list_companies(
    fund_id: str | None = None,
    status: CompanyStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    companies, total = await svc.list_companies(db, fund_id, status, skip, limit)
    return CompanyListResponse(
        companies=[_company_response(c) for c in companies],
        total=total,
    )


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    company = await svc.get_company(db, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    return _company_response(company)


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
):
    company = await svc.update_company(db, company_id, data)
    if not company:
        raise HTTPException(404, "Company not found")
    return _company_response(company)


def _fund_response(fund) -> FundResponse:
    companies = fund.companies or []
    return FundResponse(
        id=fund.id,
        name=fund.name,
        vintage_year=fund.vintage_year,
        strategy=fund.strategy,
        aum=fund.aum,
        currency=fund.currency,
        status=fund.status,
        description=fund.description,
        created_at=fund.created_at,
        updated_at=fund.updated_at,
        company_count=len(companies),
        total_invested=sum(c.initial_investment for c in companies),
        total_value=sum(c.current_valuation for c in companies),
    )


def _company_response(company) -> CompanyResponse:
    moic = company.current_valuation / company.initial_investment if company.initial_investment > 0 else 0
    return CompanyResponse(
        id=company.id,
        fund_id=company.fund_id,
        name=company.name,
        sector=company.sector,
        geography=company.geography,
        investment_date=company.investment_date,
        exit_date=company.exit_date,
        initial_investment=company.initial_investment,
        current_valuation=company.current_valuation,
        ownership_pct=company.ownership_pct,
        currency=company.currency,
        status=company.status,
        description=company.description,
        moic=round(moic, 2),
        created_at=company.created_at,
        updated_at=company.updated_at,
    )
