# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["viewer", "operator", "admin"]
ActionType = Literal[
    "create_task",
    "send_notification",
    "generate_remediation_summary",
    "call_mock_graph_endpoint",
]
ApprovalDecision = Literal["approve", "reject"]


class Citation(BaseModel):
    source: str
    excerpt: str
    score: int


class AskRequest(BaseModel):
    question: str = Field(min_length=3)


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


class ActionRequest(BaseModel):
    action_type: ActionType
    payload: dict = Field(default_factory=dict)


class ActionResponse(BaseModel):
    action_id: int
    status: Literal["completed", "pending_approval", "rejected"]
    message: str
    output: dict = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    decision: ApprovalDecision
    reviewer_notes: str | None = None


class ActionLogRecord(BaseModel):
    id: int
    timestamp_utc: datetime
    user_id: str
    role: Role
    action_type: str
    status: str
    is_sensitive: bool
    approved_by: str | None = None
    message: str
    payload: dict = Field(default_factory=dict)
    output: dict = Field(default_factory=dict)
