# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Copilot Adoption Agent"
    api_key: str = "dev-demo-key"
    db_path: str = "data/adoption.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
