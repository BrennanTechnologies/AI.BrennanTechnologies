# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

import json
from pathlib import Path
from uuid import uuid4

from app.agents.action_agent import execute_action, is_sensitive
from app.agents.knowledge_agent import answer_from_knowledge
from app.agents.router_agent import classify_intent
from app.config import Settings
from app.models import AgentStep, WorkflowRunRequest, WorkflowRunResponse
from app.services.audit import write_audit


def _load_workflow(file_path: str) -> dict:
    return json.loads(Path(file_path).read_text(encoding="utf-8"))


def run_multi_agent_workflow(request: WorkflowRunRequest, user_id: str, role: str, settings: Settings) -> WorkflowRunResponse:
    _ = _load_workflow(settings.workflow_file)
    run_id = str(uuid4())
    steps: list[AgentStep] = []

    intent = classify_intent(request.user_input)
    steps.append(
        AgentStep(
            agent_name="router_agent",
            status="completed",
            detail=f"Intent classified as {intent}.",
            output={"intent": intent},
        )
    )
    write_audit(run_id, user_id, role, "route", "completed", intent)

    if intent == "knowledge":
        knowledge_output = answer_from_knowledge(settings.knowledge_dir, request.user_input)
        steps.append(
            AgentStep(
                agent_name="knowledge_agent",
                status="completed",
                detail="Generated grounded answer with citation candidates.",
                output=knowledge_output,
            )
        )
        write_audit(run_id, user_id, role, "knowledge", "completed", "knowledge response")
        return WorkflowRunResponse(
            run_id=run_id,
            final_status="completed",
            summary="Knowledge workflow completed.",
            steps=steps,
        )

    sensitive = is_sensitive(request.user_input)
    if settings.rbac_enforced and sensitive and role != "admin":
        steps.append(
            AgentStep(
                agent_name="approval_agent",
                status="pending_approval",
                detail="Sensitive action blocked until admin approval.",
                output={"required_role": "admin"},
            )
        )
        write_audit(run_id, user_id, role, "approval_gate", "pending_approval", "sensitive action")
        return WorkflowRunResponse(
            run_id=run_id,
            final_status="pending_approval",
            summary="Action workflow paused for admin approval.",
            steps=steps,
        )

    action_output = execute_action(intent, request.user_input, request.context, settings)
    steps.append(
        AgentStep(
            agent_name="action_agent",
            status="completed",
            detail="Controlled action executed and integration hooks triggered.",
            output=action_output,
        )
    )
    write_audit(run_id, user_id, role, "action", "completed", intent)

    return WorkflowRunResponse(
        run_id=run_id,
        final_status="completed",
        summary="Action workflow completed.",
        steps=steps,
    )
