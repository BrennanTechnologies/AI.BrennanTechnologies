# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "M365 Copilot Multi-Agent Workflow"
    api_key: str = "dev-demo-key"
    workflow_file: str = "workflows/multi_agent_workflow.json"
    knowledge_dir: str = "knowledge"
    power_automate_webhook_url: str | None = None
    azure_function_url: str | None = None
    rbac_enforced: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
