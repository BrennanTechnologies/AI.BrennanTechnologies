# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["viewer", "operator", "admin"]
StepStatus = Literal["completed", "pending_approval", "skipped", "failed"]


class AgentStep(BaseModel):
    agent_name: str
    status: StepStatus
    detail: str
    output: dict = Field(default_factory=dict)


class WorkflowRunRequest(BaseModel):
    user_input: str = Field(min_length=3)
    context: dict = Field(default_factory=dict)


class WorkflowRunResponse(BaseModel):
    run_id: str
    final_status: Literal["completed", "pending_approval", "blocked"]
    summary: str
    steps: list[AgentStep]


class AuditRecord(BaseModel):
    timestamp_utc: datetime
    run_id: str
    user_id: str
    role: Role
    event: str
    status: str
    detail: str
