# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com


def classify_intent(user_input: str) -> str:
    text = user_input.lower()
    if any(k in text for k in ["policy", "retention", "governance", "sharepoint"]):
        return "knowledge"
    if any(k in text for k in ["notify", "alert", "teams", "email"]):
        return "notification"
    if any(k in text for k in ["task", "ticket", "follow up", "planner"]):
        return "task"
    if any(k in text for k in ["remediate", "summary", "incident"]):
        return "remediation"
    return "general_action"
