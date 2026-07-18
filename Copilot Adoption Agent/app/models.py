# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SkillLevel = Literal["beginner", "intermediate", "advanced"]


class AdoptionEventIn(BaseModel):
    user_id: str = Field(min_length=3)
    department: str = Field(min_length=2)
    action: str = Field(min_length=3)


class CoachRequest(BaseModel):
    user_id: str = Field(min_length=3)
    role: str = Field(min_length=2)
    goal: str = Field(min_length=5)
    skill_level: SkillLevel = "beginner"


class PromptRecommendation(BaseModel):
    title: str
    prompt: str


class CoachResponse(BaseModel):
    teaching_tip: str
    coaching_message: str
    prompt_recommendations: list[PromptRecommendation]
    training_path: list[str]


class AdoptionMetrics(BaseModel):
    total_events: int
    active_users_30d: int
    top_departments: list[dict]


class CoachingSession(BaseModel):
    timestamp_utc: datetime
    user_id: str
    role: str
    goal: str
    skill_level: SkillLevel
