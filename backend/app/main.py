from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import portfolio, documents, monitoring, valuation, reports

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered private markets operations platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)
app.include_router(documents.router)
app.include_router(monitoring.router)
app.include_router(valuation.router)
app.include_router(reports.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
