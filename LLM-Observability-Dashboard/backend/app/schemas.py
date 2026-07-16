# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventIn(BaseModel):
    timestamp: datetime
    request_id: str = Field(min_length=3, max_length=100)
    model: str
    provider: str
    status: str
    latency_ms: int = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0)
    input: str | None = None
    output: str | None = None
    metadata: dict[str, Any] | None = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    request_id: str
    model: str
    provider: str
    status: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    input: str | None
    output: str | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="extra_metadata")


class SummaryMetrics(BaseModel):
    total_requests: int
    success_rate_pct: float
    error_rate_pct: float
    p50_latency_ms: float
    p95_latency_ms: float
    total_tokens: int
    total_cost_usd: float


class TimeseriesPoint(BaseModel):
    bucket_start: str
    avg_latency_ms: float
    error_rate_pct: float
    requests: int
