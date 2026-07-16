# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models import LLMEvent
from app.schemas import EventIn, SummaryMetrics, TimeseriesPoint


def create_event(db: Session, payload: EventIn) -> LLMEvent:
    total_tokens = payload.prompt_tokens + payload.completion_tokens
    event = LLMEvent(
        timestamp=payload.timestamp,
        request_id=payload.request_id,
        model=payload.model,
        provider=payload.provider,
        status=payload.status,
        latency_ms=payload.latency_ms,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
        total_tokens=total_tokens,
        cost_usd=payload.cost_usd,
        input=payload.input,
        output=payload.output,
        extra_metadata=payload.metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_traces(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    model: str | None = None,
) -> list[LLMEvent]:
    query = db.query(LLMEvent).order_by(LLMEvent.timestamp.desc())
    if status:
        query = query.filter(LLMEvent.status == status)
    if model:
        query = query.filter(LLMEvent.model == model)
    return query.offset(offset).limit(limit).all()


def _percentile(values: list[int], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = int(round((len(values) - 1) * p))
    return float(values[idx])


def summary_metrics(db: Session, window_minutes: int) -> SummaryMetrics:
    now = datetime.now(UTC).replace(tzinfo=None)
    since = now - timedelta(minutes=window_minutes)

    events = db.query(LLMEvent).filter(LLMEvent.timestamp >= since).all()
    total_requests = len(events)
    if total_requests == 0:
        return SummaryMetrics(
            total_requests=0,
            success_rate_pct=0,
            error_rate_pct=0,
            p50_latency_ms=0,
            p95_latency_ms=0,
            total_tokens=0,
            total_cost_usd=0,
        )

    success_count = sum(1 for e in events if e.status == "success")
    error_count = total_requests - success_count
    latencies = [e.latency_ms for e in events]
    token_sum = sum(e.total_tokens for e in events)
    cost_sum = sum(e.cost_usd for e in events)

    return SummaryMetrics(
        total_requests=total_requests,
        success_rate_pct=round((success_count / total_requests) * 100, 2),
        error_rate_pct=round((error_count / total_requests) * 100, 2),
        p50_latency_ms=round(_percentile(latencies, 0.50), 2),
        p95_latency_ms=round(_percentile(latencies, 0.95), 2),
        total_tokens=token_sum,
        total_cost_usd=round(cost_sum, 4),
    )


def timeseries_metrics(
    db: Session,
    window_minutes: int,
    bucket_seconds: int,
) -> list[TimeseriesPoint]:
    now = datetime.now(UTC).replace(tzinfo=None)
    since = now - timedelta(minutes=window_minutes)

    epoch_bucket = func.strftime(
        "%Y-%m-%dT%H:%M:%S",
        (func.strftime("%s", LLMEvent.timestamp) / bucket_seconds) * bucket_seconds,
        "unixepoch",
    )

    rows = (
        db.query(
            epoch_bucket.label("bucket_start"),
            func.avg(LLMEvent.latency_ms).label("avg_latency"),
            func.sum(case((LLMEvent.status != "success", 1), else_=0)).label("errors"),
            func.count(LLMEvent.id).label("requests"),
        )
        .filter(LLMEvent.timestamp >= since)
        .group_by("bucket_start")
        .order_by("bucket_start")
        .all()
    )

    points: list[TimeseriesPoint] = []
    for row in rows:
        requests = int(row.requests or 0)
        errors = int(row.errors or 0)
        error_rate = (errors / requests) * 100 if requests else 0.0
        points.append(
            TimeseriesPoint(
                bucket_start=row.bucket_start,
                avg_latency_ms=round(float(row.avg_latency or 0), 2),
                error_rate_pct=round(error_rate, 2),
                requests=requests,
            )
        )

    return points
