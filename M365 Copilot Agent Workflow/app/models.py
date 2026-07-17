# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["viewer", "operator", "admin"]


class WorkflowRequest(BaseModel):
    user_input: str = Field(min_length=3)
    context: dict = Field(default_factory=dict)


class WorkflowStepResult(BaseModel):
    step_name: str
    status: Literal["completed", "pending_approval", "skipped"]
    detail: str
    output: dict = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    run_id: str
    final_status: Literal["completed", "pending_approval", "blocked"]
    summary: str
    steps: list[WorkflowStepResult]


class AuditRecord(BaseModel):
    run_id: str
    timestamp_utc: datetime
    user_id: str
    role: Role
    action: str
    status: str
    detail: str
