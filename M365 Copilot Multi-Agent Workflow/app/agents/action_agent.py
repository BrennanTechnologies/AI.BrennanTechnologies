# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from app.config import Settings
from app.services.integrations import call_integrations

SENSITIVE_WORDS = {"disable", "delete", "revoke", "block", "remove"}


def is_sensitive(text: str) -> bool:
    return len(set(text.lower().split()).intersection(SENSITIVE_WORDS)) > 0


def execute_action(intent: str, user_input: str, context: dict, settings: Settings) -> dict:
    payload = {
        "intent": intent,
        "request": user_input,
        "context": context,
        "status": "executed",
    }
    integration_results = call_integrations(settings, payload)
    payload.update(integration_results)
    return payload
