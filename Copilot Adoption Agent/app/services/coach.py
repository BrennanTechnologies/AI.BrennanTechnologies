# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from app.models import CoachRequest, CoachResponse, PromptRecommendation


ROLE_PROMPTS: dict[str, list[PromptRecommendation]] = {
    "sales": [
        PromptRecommendation(
            title="Account Brief",
            prompt="Summarize the latest customer notes and create a 5-bullet account brief with risks and next steps.",
        ),
        PromptRecommendation(
            title="Follow-up Email",
            prompt="Draft a concise follow-up email from this meeting transcript, including action items and owners.",
        ),
    ],
    "hr": [
        PromptRecommendation(
            title="Policy Summary",
            prompt="Summarize this HR policy into plain language and provide a 10-question FAQ.",
        ),
        PromptRecommendation(
            title="Onboarding Checklist",
            prompt="Create a role-based onboarding checklist for a new hire in this department.",
        ),
    ],
    "it": [
        PromptRecommendation(
            title="Incident Triage",
            prompt="Analyze this incident thread and produce triage summary, severity, and immediate next actions.",
        ),
        PromptRecommendation(
            title="Change Review",
            prompt="Review this change request and highlight risks, dependencies, rollback plan, and owner actions.",
        ),
    ],
}


TRAINING_PATHS = {
    "beginner": [
        "Copilot Fundamentals: prompting basics",
        "Prompt patterns: summarize, rewrite, extract",
        "Responsible AI and data handling",
    ],
    "intermediate": [
        "Role-based prompt engineering",
        "Copilot in Teams and SharePoint workflows",
        "Quality checks and citation habits",
    ],
    "advanced": [
        "Agentic workflows and action orchestration",
        "Governance, security, and approval gates",
        "Telemetry and adoption optimization",
    ],
}


def build_coaching_response(request: CoachRequest) -> CoachResponse:
    role_key = request.role.lower().strip()
    prompt_set = ROLE_PROMPTS.get(role_key, ROLE_PROMPTS.get("it", []))
    training_path = TRAINING_PATHS[request.skill_level]

    teaching_tip = (
        "Use a 4-part prompt structure: context, task, constraints, and output format. "
        "This consistently improves Copilot response quality."
    )
    coaching_message = (
        f"For goal '{request.goal}', start with one focused prompt and iterate using explicit constraints. "
        "Track what worked in a shared prompt library to accelerate team adoption."
    )

    return CoachResponse(
        teaching_tip=teaching_tip,
        coaching_message=coaching_message,
        prompt_recommendations=prompt_set,
        training_path=training_path,
    )
