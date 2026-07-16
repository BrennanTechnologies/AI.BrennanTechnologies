# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com


from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, engine, get_db
from app.seed import seed_events

app = FastAPI(title="LLM Observability API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/events", response_model=schemas.EventOut)
def ingest_event(payload: schemas.EventIn, db: Session = Depends(get_db)) -> schemas.EventOut:
    try:
        return crud.create_event(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="request_id already exists") from exc


@app.get("/api/traces", response_model=list[schemas.EventOut])
def traces(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    model: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[schemas.EventOut]:
    return crud.list_traces(db, limit=limit, offset=offset, status=status, model=model)


@app.get("/api/metrics/summary", response_model=schemas.SummaryMetrics)
def metrics_summary(
    window_minutes: int = Query(default=60, ge=1, le=24 * 60),
    db: Session = Depends(get_db),
) -> schemas.SummaryMetrics:
    return crud.summary_metrics(db, window_minutes=window_minutes)


@app.get("/api/metrics/timeseries", response_model=list[schemas.TimeseriesPoint])
def metrics_timeseries(
    window_minutes: int = Query(default=180, ge=5, le=24 * 60),
    bucket_seconds: int = Query(default=300, ge=60, le=3600),
    db: Session = Depends(get_db),
) -> list[schemas.TimeseriesPoint]:
    return crud.timeseries_metrics(
        db,
        window_minutes=window_minutes,
        bucket_seconds=bucket_seconds,
    )


@app.post("/api/seed")
def seed(db: Session = Depends(get_db)) -> dict[str, int]:
    inserted = seed_events(db)
    return {"inserted": inserted}
