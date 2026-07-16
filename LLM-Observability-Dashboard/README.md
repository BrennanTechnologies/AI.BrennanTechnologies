![Brennan Technologies Logo](./resources/Brennan_Technologies_LLC-small2.png)

# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

# LLM Observability Dashboard

A full-stack observability dashboard for tracking LLM request health, latency, token usage, cost, and error rates.

## Stack

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React + TypeScript + Vite + Recharts
- Local orchestration: Docker Compose

## Features

- Ingest LLM events via API
- View KPI cards: total requests, p95 latency, error rate, token usage, estimated cost
- Trace table with filtering by model/status
- Latency and error-rate time series
- Seed data for instant local demo

## Quick Start (Local)

### 1) Backend

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

Backend is available at `http://localhost:8000`.

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend is available at `http://localhost:5173`.

### 3) Seed sample data

```bash
curl -X POST http://localhost:8000/api/seed
```

## Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Ingest API Example

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-07-16T15:01:00Z",
    "request_id": "req_123",
    "model": "gpt-4.1-mini",
    "provider": "openai",
    "status": "success",
    "latency_ms": 842,
    "prompt_tokens": 512,
    "completion_tokens": 143,
    "cost_usd": 0.0132,
    "input": "Summarize this article",
    "output": "Here is a concise summary...",
    "metadata": {"team": "growth", "feature": "copilot-help"}
  }'
```

## API Endpoints

- `GET /health`
- `POST /api/events`
- `GET /api/traces`
- `GET /api/metrics/summary`
- `GET /api/metrics/timeseries`
- `POST /api/seed`
