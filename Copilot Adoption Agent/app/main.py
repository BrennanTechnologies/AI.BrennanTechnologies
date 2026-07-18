# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import AdoptionEventIn, AdoptionMetrics, CoachRequest, CoachResponse, CoachingSession
from app.services.coach import build_coaching_response
from app.services.db import get_metrics, init_db, insert_adoption_event, insert_coaching_session
from app.services.security import require_api_key

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db(settings)


@app.get("/")
def root() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/api/coach", response_model=CoachResponse)
def coach(request: CoachRequest, _: None = Depends(require_api_key)) -> CoachResponse:
    response = build_coaching_response(request)
    insert_coaching_session(
        settings,
        CoachingSession(
            timestamp_utc=datetime.now(timezone.utc),
            user_id=request.user_id,
            role=request.role,
            goal=request.goal,
            skill_level=request.skill_level,
        ),
        response.model_dump(),
    )
    return response


@app.post("/api/adoption/events")
def add_event(event: AdoptionEventIn, _: None = Depends(require_api_key)) -> dict:
    insert_adoption_event(settings, event.user_id, event.department, event.action)
    return {"status": "logged"}


@app.get("/api/adoption/metrics", response_model=AdoptionMetrics)
def adoption_metrics(_: None = Depends(require_api_key)) -> AdoptionMetrics:
    metrics = get_metrics(settings)
    return AdoptionMetrics(**metrics)
