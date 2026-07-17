# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime, timezone
from typing import Any

from app.config import Settings
from app.models import ActionRequest
from app.services import db
from app.services.integrations import notify_integrations

ACTION_POLICY: dict[str, dict[str, Any]] = {
    "create_task": {"min_role": "operator", "sensitive": False, "approval_required": False},
    "send_notification": {"min_role": "operator", "sensitive": False, "approval_required": False},
    "generate_remediation_summary": {"min_role": "operator", "sensitive": False, "approval_required": False},
    "call_mock_graph_endpoint": {"min_role": "operator", "sensitive": True, "approval_required": True},
}


def role_allows(user_role: str, min_role: str) -> bool:
    ranks = {"viewer": 1, "operator": 2, "admin": 3}
    return ranks[user_role] >= ranks[min_role]


def _mock_execute_action(action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if action_type == "create_task":
        return {
            "task_id": f"tsk-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "title": payload.get("title", "Follow up governance control"),
            "owner": payload.get("owner", "governance-ops"),
            "status": "created",
        }

    if action_type == "send_notification":
        return {
            "channel": payload.get("channel", "teams://governance"),
            "message": payload.get("message", "Governance action completed."),
            "status": "sent",
        }

    if action_type == "generate_remediation_summary":
        issue = payload.get("issue", "Unknown policy gap")
        return {
            "summary": (
                f"Remediation summary: investigate '{issue}', assign owner, set due date, "
                "and track closure evidence in SharePoint governance library."
            ),
            "status": "generated",
        }

    if action_type == "call_mock_graph_endpoint":
        return {
            "endpoint": payload.get("endpoint", "/mock/graph/users/{id}/block-signin"),
            "target": payload.get("target", "user@contoso.com"),
            "result": "mock_graph_operation_completed",
        }

    return {"status": "unknown_action"}


def create_action_log(
    settings: Settings,
    *,
    user_id: str,
    role: str,
    request: ActionRequest,
) -> tuple[int, dict[str, Any], dict[str, Any]]:
    policy = ACTION_POLICY[request.action_type]

    if not role_allows(role, policy["min_role"]):
        raise PermissionError(f"Action requires role {policy['min_role']} or above.")

    timestamp = datetime.now(timezone.utc).isoformat()

    if policy["approval_required"]:
        action_id = db.insert_log(
            settings,
            timestamp_utc=timestamp,
            user_id=user_id,
            role=role,
            action_type=request.action_type,
            status="pending_approval",
            is_sensitive=bool(policy["sensitive"]),
            approved_by=None,
            message="Awaiting admin approval for sensitive action.",
            payload=request.payload,
            output={},
        )
        return action_id, {"status": "pending_approval"}, policy

    output = _mock_execute_action(request.action_type, request.payload)
    integration_result = notify_integrations(
        settings,
        {
            "action_type": request.action_type,
            "user_id": user_id,
            "payload": request.payload,
            "output": output,
        },
    )
    output.update(integration_result)

    action_id = db.insert_log(
        settings,
        timestamp_utc=timestamp,
        user_id=user_id,
        role=role,
        action_type=request.action_type,
        status="completed",
        is_sensitive=bool(policy["sensitive"]),
        approved_by=None,
        message="Action completed successfully.",
        payload=request.payload,
        output=output,
    )
    return action_id, output, policy


def apply_approval(
    settings: Settings,
    *,
    action_id: int,
    reviewer: str,
    decision: str,
    reviewer_notes: str | None,
) -> dict[str, Any]:
    row = db.get_log(settings, action_id)
    if row is None:
        raise ValueError("Action not found.")

    if row["status"] != "pending_approval":
        raise ValueError("Action is not pending approval.")

    payload = row["payload_json"]
    import json

    payload_obj = json.loads(payload)
    action_type = row["action_type"]

    if decision == "reject":
        output = {"status": "rejected", "reviewer_notes": reviewer_notes}
        db.update_log_status(
            settings,
            action_id,
            status="rejected",
            approved_by=reviewer,
            message=reviewer_notes or "Rejected by admin reviewer.",
            output=output,
        )
        return output

    output = _mock_execute_action(action_type, payload_obj)
    integration_result = notify_integrations(
        settings,
        {
            "action_id": action_id,
            "action_type": action_type,
            "approved_by": reviewer,
            "payload": payload_obj,
            "output": output,
        },
    )
    output.update(integration_result)
    if reviewer_notes:
        output["reviewer_notes"] = reviewer_notes

    db.update_log_status(
        settings,
        action_id,
        status="completed",
        approved_by=reviewer,
        message="Approved and executed by admin reviewer.",
        output=output,
    )
    return output
