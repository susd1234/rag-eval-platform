"""
Configuration management for AI SME Evaluation Platform
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application settings
    port: int = 9777
    environment: Literal["development", "production"] = "development"

    # Model configuration
    model_provider: Literal["gpt", "claude"] = "gpt"
    gpt_model: str = "gpt-4o-mini"
    claude_model: str = "claude-3-sonnet-20240229"

    # LiteLLM configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    litellm_proxy_url: str = ""

    # AutoGen configuration
    autogen_temperature: float = 0.1
    autogen_max_tokens: int = 2000

    # Evaluation settings
    max_concurrent_evaluations: int = 5
    evaluation_timeout: int = 300  # seconds

    # Agent communication settings
    agent_communication_timeout: int = 25  # seconds per agent (more aggressive)
    llm_request_timeout: int = 20  # seconds per LLM call (more aggressive)
    agent_retry_attempts: int = 1  # Reduced retries for faster failure detection
    agent_retry_delay: float = 0.5  # seconds (reduced delay)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()
