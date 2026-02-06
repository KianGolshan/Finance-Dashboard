import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.financial_metric import MetricType
from app.schemas.monitoring import (
    MetricCreate,
    MetricResponse,
    MetricListResponse,
    MetricTimeSeries,
    ScenarioCreate,
    ScenarioResponse,
)
from app.services import monitoring as svc

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.post("/metrics", response_model=MetricResponse, status_code=201)
async def create_metric(data: MetricCreate, db: AsyncSession = Depends(get_db)):
    metric = await svc.create_metric(db, data)
    return MetricResponse.model_validate(metric)


@router.get("/metrics/{company_id}", response_model=MetricListResponse)
async def list_metrics(
    company_id: str,
    metric_type: MetricType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    metrics, total = await svc.list_metrics(db, company_id, metric_type, start_date, end_date, skip, limit)
    return MetricListResponse(
        metrics=[MetricResponse.model_validate(m) for m in metrics],
        total=total,
    )


@router.get("/metrics/{company_id}/timeseries", response_model=MetricTimeSeries)
async def get_time_series(
    company_id: str,
    metric_type: MetricType = Query(...),
    db: AsyncSession = Depends(get_db),
):
    data_points = await svc.get_time_series(db, company_id, metric_type)
    return MetricTimeSeries(metric_type=metric_type, data_points=data_points)


@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)
async def create_scenario(data: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    scenario = await svc.create_scenario(db, data)
    return ScenarioResponse.model_validate(scenario)


@router.get("/scenarios/{company_id}", response_model=list[ScenarioResponse])
async def list_scenarios(
    company_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    scenarios, _ = await svc.list_scenarios(db, company_id, skip, limit)
    return [ScenarioResponse.model_validate(s) for s in scenarios]
