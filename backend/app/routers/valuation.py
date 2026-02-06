import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.valuation import (
    ValuationCreate,
    ValuationResponse,
    ValuationListResponse,
    OverrideCreate,
    OverrideResponse,
)
from app.services import valuation_engine as svc

router = APIRouter(prefix="/api/valuation", tags=["Valuation"])


@router.post("/run", response_model=ValuationResponse, status_code=201)
async def run_valuation(data: ValuationCreate, db: AsyncSession = Depends(get_db)):
    valuation = await svc.create_valuation(db, data)
    return ValuationResponse.model_validate(valuation)


@router.get("", response_model=ValuationListResponse)
async def list_valuations(
    company_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    valuations, total = await svc.list_valuations(db, company_id, skip, limit)
    return ValuationListResponse(
        valuations=[ValuationResponse.model_validate(v) for v in valuations],
        total=total,
    )


@router.get("/{valuation_id}", response_model=ValuationResponse)
async def get_valuation(valuation_id: str, db: AsyncSession = Depends(get_db)):
    valuation = await svc.get_valuation(db, valuation_id)
    if not valuation:
        raise HTTPException(404, "Valuation not found")
    return ValuationResponse.model_validate(valuation)


@router.post("/{valuation_id}/overrides", response_model=OverrideResponse, status_code=201)
async def add_override(
    valuation_id: str,
    data: OverrideCreate,
    db: AsyncSession = Depends(get_db),
):
    valuation = await svc.get_valuation(db, valuation_id)
    if not valuation:
        raise HTTPException(404, "Valuation not found")
    override = await svc.add_override(db, valuation_id, data)
    return OverrideResponse.model_validate(override)
