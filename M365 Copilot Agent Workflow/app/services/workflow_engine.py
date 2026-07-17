# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

import json
from pathlib import Path
from uuid import uuid4

from app.config import Settings
from app.models import WorkflowRequest, WorkflowResponse, WorkflowStepResult
from app.services.audit import log_event
from app.services.integrations import trigger_integrations
from app.services.security import ensure_role

SENSITIVE_KEYWORDS = {"disable", "block", "delete", "revoke", "remove"}


def _load_workflow(path: str) -> dict:
    data = Path(path).read_text(encoding="utf-8")
    return json.loads(data)


def _classify_intent(user_input: str) -> str:
    text = user_input.lower()
    if any(word in text for word in ["policy", "governance", "rule", "retention"]):
        return "knowledge_query"
    if any(word in text for word in ["notify", "message", "alert", "teams"]):
        return "notification_action"
    if any(word in text for word in ["task", "ticket", "follow up"]):
        return "task_action"
    if any(word in text for word in ["remediate", "remediation", "summary"]):
        return "remediation_action"
    return "general_action"


def _is_sensitive(user_input: str) -> bool:
    tokens = set(user_input.lower().split())
    return len(tokens.intersection(SENSITIVE_KEYWORDS)) > 0


def execute_workflow(
    request: WorkflowRequest,
    *,
    user_id: str,
    role: str,
    settings: Settings,
) -> WorkflowResponse:
    _ = _load_workflow(settings.workflow_definition)
    run_id = str(uuid4())
    steps: list[WorkflowStepResult] = []

    intent = _classify_intent(request.user_input)
    steps.append(
        WorkflowStepResult(
            step_name="intent_classification",
            status="completed",
            detail=f"Intent classified as {intent}.",
            output={"intent": intent},
        )
    )
    log_event(run_id, user_id, role, "intent_classification", "completed", intent)

    if intent == "knowledge_query":
        summary = "Answer generated from governance knowledge with Copilot-compatible grounding path."
        steps.append(
            WorkflowStepResult(
                step_name="knowledge_response",
                status="completed",
                detail="Knowledge response prepared.",
                output={"answer": "Policy response generated.", "citations": ["governance_policy.md"]},
            )
        )
        log_event(run_id, user_id, role, "knowledge_response", "completed", "governance answer")
        return WorkflowResponse(run_id=run_id, final_status="completed", summary=summary, steps=steps)

    ensure_role(role, "operator")

    sensitive = _is_sensitive(request.user_input)
    if settings.rbac_enforced and sensitive and role != "admin":
        steps.append(
            WorkflowStepResult(
                step_name="approval_gate",
                status="pending_approval",
                detail="Sensitive operation requires admin approval.",
                output={"required_role": "admin"},
            )
        )
        log_event(run_id, user_id, role, "approval_gate", "pending_approval", "sensitive action")
        return WorkflowResponse(
            run_id=run_id,
            final_status="pending_approval",
            summary="Workflow paused pending admin approval.",
            steps=steps,
        )

    action_payload = {
        "run_id": run_id,
        "intent": intent,
        "user_input": request.user_input,
        "context": request.context,
        "actor": {"user_id": user_id, "role": role},
    }
    integration_output = trigger_integrations(settings, action_payload)

    steps.append(
        WorkflowStepResult(
            step_name="execute_action",
            status="completed",
            detail="Controlled action executed.",
            output={"action_payload": action_payload, "integration_output": integration_output},
        )
    )
    log_event(run_id, user_id, role, "execute_action", "completed", intent)

    return WorkflowResponse(
        run_id=run_id,
        final_status="completed",
        summary="Workflow executed with governance controls and audit logging.",
        steps=steps,
    )
