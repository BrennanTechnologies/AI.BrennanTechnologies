# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime

from fastapi import Depends, FastAPI, Query

from app.config import get_settings
from app.models import AuditRecord, WorkflowRequest, WorkflowResponse
from app.services.audit import read_audit
from app.services.security import UserContext, get_user_context
from app.services.workflow_engine import execute_workflow

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "time_utc": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/workflow/run", response_model=WorkflowResponse)
def run_workflow(payload: WorkflowRequest, user: UserContext = Depends(get_user_context)) -> WorkflowResponse:
    return execute_workflow(payload, user_id=user.user_id, role=user.role, settings=settings)


@app.get("/workflow/audit", response_model=list[AuditRecord])
def workflow_audit(
    limit: int = Query(default=100, ge=1, le=500),
    _: UserContext = Depends(get_user_context),
) -> list[AuditRecord]:
    return read_audit(limit=limit)
