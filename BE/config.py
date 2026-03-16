"""Runtime configuration for the research agent."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    """Settings loaded from environment variables."""
    # Agentica
    agentica_api_key: str = Field(default_factory=lambda: os.getenv("AGENTICA_API_KEY", ""))

    # AWS (Bedrock / ingest pipeline)
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")

    # Optional tool APIs
    openalex_email: str = Field(default_factory=lambda: os.getenv("OPENALEX_EMAIL", ""))
    openalex_api_key: str = Field(default_factory=lambda: os.getenv("OPENALEX_API_KEY", ""))
    kernel_api_key: str = Field(default_factory=lambda: os.getenv("KERNEL_API_KEY", ""))
    tinyfish_api_key: str = Field(default_factory=lambda: os.getenv("TINYFISH_API_KEY", ""))


settings = Settings()
