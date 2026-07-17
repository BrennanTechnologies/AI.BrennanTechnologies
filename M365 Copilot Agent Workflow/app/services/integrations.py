# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from typing import Any

import httpx

from app.config import Settings


def trigger_integrations(settings: Settings, payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    with httpx.Client(timeout=10.0) as client:
        if settings.power_automate_webhook_url:
            res = client.post(settings.power_automate_webhook_url, json=payload)
            result["power_automate_status"] = res.status_code
        if settings.azure_function_url:
            res = client.post(settings.azure_function_url, json=payload)
            result["azure_function_status"] = res.status_code
    return result
