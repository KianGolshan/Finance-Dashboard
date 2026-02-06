import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_and_list_funds(client: AsyncClient):
    # Create fund
    res = await client.post("/api/portfolio/funds", json={
        "name": "Test Growth Fund I",
        "vintage_year": 2024,
        "strategy": "growth_equity",
        "aum": 500_000_000,
    })
    assert res.status_code == 201
    fund = res.json()
    assert fund["name"] == "Test Growth Fund I"
    assert fund["strategy"] == "growth_equity"
    fund_id = fund["id"]

    # List funds
    res = await client.get("/api/portfolio/funds")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(f["id"] == fund_id for f in data["funds"])

    # Get single fund
    res = await client.get(f"/api/portfolio/funds/{fund_id}")
    assert res.status_code == 200
    assert res.json()["id"] == fund_id

    # Update fund
    res = await client.patch(f"/api/portfolio/funds/{fund_id}", json={"aum": 600_000_000})
    assert res.status_code == 200
    assert res.json()["aum"] == 600_000_000


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient):
    # Create fund first
    fund_res = await client.post("/api/portfolio/funds", json={
        "name": "Company Test Fund",
        "vintage_year": 2023,
        "strategy": "buyout",
    })
    fund_id = fund_res.json()["id"]

    # Create company
    res = await client.post("/api/portfolio/companies", json={
        "fund_id": fund_id,
        "name": "TechCo Inc",
        "sector": "technology",
        "geography": "North America",
        "investment_date": "2023-06-15",
        "initial_investment": 50_000_000,
        "current_valuation": 75_000_000,
        "ownership_pct": 35.0,
    })
    assert res.status_code == 201
    company = res.json()
    assert company["name"] == "TechCo Inc"
    assert company["moic"] == 1.5

    # List companies
    res = await client.get("/api/portfolio/companies")
    assert res.status_code == 200
    assert res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_portfolio_summary(client: AsyncClient):
    res = await client.get("/api/portfolio/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_nav" in data
    assert "gross_moic" in data


@pytest.mark.asyncio
async def test_fund_not_found(client: AsyncClient):
    res = await client.get("/api/portfolio/funds/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
