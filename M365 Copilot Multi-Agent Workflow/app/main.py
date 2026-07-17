# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime

from fastapi import Depends, FastAPI, Query

from app.config import get_settings
from app.models import AuditRecord, WorkflowRunRequest, WorkflowRunResponse
from app.services.audit import read_audit
from app.services.orchestrator import run_multi_agent_workflow
from app.services.security import UserContext, get_user_context

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "time_utc": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/workflow/run", response_model=WorkflowRunResponse)
def run_workflow(payload: WorkflowRunRequest, user: UserContext = Depends(get_user_context)) -> WorkflowRunResponse:
    return run_multi_agent_workflow(payload, user.user_id, user.role, settings)


@app.get("/workflow/audit", response_model=list[AuditRecord])
def list_audit(limit: int = Query(default=100, ge=1, le=500), _: UserContext = Depends(get_user_context)) -> list[AuditRecord]:
    return read_audit(limit=limit)
