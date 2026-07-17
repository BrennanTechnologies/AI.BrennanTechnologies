# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

import json
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query

from app.config import get_settings
from app.models import ActionLogRecord, ActionRequest, ActionResponse, ApprovalRequest, AskRequest, AskResponse
from app.services import actions as action_service
from app.services import db
from app.services.rag import answer_question
from app.services.security import UserContext, get_user_context

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    db.init_db(settings)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "time_utc": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/agent/ask", response_model=AskResponse)
def agent_ask(payload: AskRequest, user: UserContext = Depends(get_user_context)) -> AskResponse:
    _ = user
    return answer_question(payload.question, settings)


@app.post("/agent/action", response_model=ActionResponse)
def agent_action(payload: ActionRequest, user: UserContext = Depends(get_user_context)) -> ActionResponse:
    try:
        action_id, output, policy = action_service.create_action_log(
            settings,
            user_id=user.user_id,
            role=user.role,
            request=payload,
        )
    except PermissionError as ex:
        raise HTTPException(status_code=403, detail=str(ex)) from ex

    if policy["approval_required"]:
        return ActionResponse(
            action_id=action_id,
            status="pending_approval",
            message="Action recorded and pending admin approval.",
            output=output,
        )

    return ActionResponse(
        action_id=action_id,
        status="completed",
        message="Action executed and logged.",
        output=output,
    )


@app.post("/agent/approvals/{action_id}", response_model=ActionResponse)
def approve_action(
    action_id: int,
    payload: ApprovalRequest,
    user: UserContext = Depends(get_user_context),
) -> ActionResponse:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can approve/reject sensitive actions.")

    try:
        output = action_service.apply_approval(
            settings,
            action_id=action_id,
            reviewer=user.user_id,
            decision=payload.decision,
            reviewer_notes=payload.reviewer_notes,
        )
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex

    status = "completed" if payload.decision == "approve" else "rejected"
    return ActionResponse(
        action_id=action_id,
        status=status,
        message=f"Action {payload.decision}d by admin and logged.",
        output=output,
    )


@app.get("/agent/actions/logs", response_model=list[ActionLogRecord])
def get_action_logs(
    limit: int = Query(default=100, ge=1, le=500),
    user: UserContext = Depends(get_user_context),
) -> list[ActionLogRecord]:
    if user.role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator or admin role required.")

    rows = db.list_logs(settings, limit=limit)
    records: list[ActionLogRecord] = []
    for row in rows:
        records.append(
            ActionLogRecord(
                id=row["id"],
                timestamp_utc=datetime.fromisoformat(row["timestamp_utc"]),
                user_id=row["user_id"],
                role=row["role"],
                action_type=row["action_type"],
                status=row["status"],
                is_sensitive=bool(row["is_sensitive"]),
                approved_by=row["approved_by"],
                message=row["message"],
                payload=json.loads(row["payload_json"]),
                output=json.loads(row["output_json"]),
            )
        )
    return records


@app.post("/mock/graph/remediate")
def mock_graph_remediate(payload: dict, user: UserContext = Depends(get_user_context)) -> dict:
    if user.role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator or admin role required.")

    return {
        "status": "ok",
        "message": "Mock Graph endpoint accepted remediation request.",
        "received": payload,
    }
