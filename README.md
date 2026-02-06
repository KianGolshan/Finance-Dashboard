# Meridian — Private Markets Operations Platform

AI-powered portfolio monitoring, valuation, and document extraction platform for private markets investment teams.

## Architecture

```
Frontend (Next.js 14) → API Gateway (FastAPI) → PostgreSQL + ChromaDB
                                                 ↕
                                            AI Pipeline (LLM extraction, embeddings)
```

### Core Modules

| Module | Description |
|---|---|
| **Portfolio** | Fund/company registry, ownership tracking, performance metrics |
| **Documents** | Upload, parse, and extract structured data from financial documents |
| **Monitoring** | KPI tracking, time-series metrics, scenario analysis engine |
| **Valuation** | DCF, comparable companies, sensitivity modeling with override support |
| **Reports** | Templated report generation, audit logging, version tracking |

## Tech Stack

- **Frontend**: Next.js 14, React 18, Tailwind CSS, Recharts, Lucide Icons
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: PostgreSQL 16, ChromaDB (vector embeddings)
- **AI**: OpenAI GPT-4o (extraction), rule-based fallback, embedding search

## Quick Start

### With Docker

```bash
docker compose up -d
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your settings
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Seed sample data:**

```bash
cd backend
python seed.py
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/portfolio/summary` | Portfolio aggregates |
| CRUD | `/api/portfolio/funds` | Fund management |
| CRUD | `/api/portfolio/companies` | Company management |
| POST | `/api/documents/upload` | Upload document |
| POST | `/api/documents/{id}/extract` | Run AI extraction |
| GET | `/api/monitoring/metrics/{company_id}` | Financial metrics |
| POST | `/api/monitoring/scenarios` | Run scenario analysis |
| POST | `/api/valuation/run` | Execute valuation model |
| GET/POST | `/api/reports` | Report generation |
| GET | `/api/reports/audit-log` | Audit trail |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── models/           # SQLAlchemy ORM (9 models)
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API endpoints (5 routers)
│   │   ├── services/         # Business logic
│   │   └── ai/               # Document parser, LLM extractor, embeddings
│   ├── tests/                # pytest suite
│   ├── alembic/              # DB migrations
│   └── seed.py               # Sample data
├── frontend/
│   └── src/
│       ├── app/              # Next.js pages (7 views)
│       ├── components/       # React components
│       ├── lib/              # API client, types, utilities
│       └── hooks/            # Custom React hooks
└── docker-compose.yml
```
