# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    azure_openai_endpoint: str
    azure_openai_chat_deployment: str
    azure_openai_embedding_deployment: str
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_api_key: str | None = None

    azure_search_endpoint: str
    azure_search_index_name: str = "enterprise-docs"
    azure_search_api_key: str | None = None

    top_k: int = 5
    similarity_threshold: float = 0.2
    chunk_size: int = 1200
    chunk_overlap: int = 200
    upload_dir: str = "uploads"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
