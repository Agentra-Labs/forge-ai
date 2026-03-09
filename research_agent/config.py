"""Configuration and data models for the research agent."""

from __future__ import annotations

import os
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ResearchMode(str, Enum):
    DEEP = "deep"
    WIDE = "wide"
    CHAINED = "chained"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class PaperMeta(BaseModel):
    """Lightweight paper metadata returned by Wide Researcher."""
    arxiv_id: Optional[str] = None
    ss_id: Optional[str] = None
    openalex_id: Optional[str] = None
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    url: str = ""
    year: Optional[int] = None
    citation_count: Optional[int] = None
    venue: Optional[str] = None


class PaperReview(PaperMeta):
    """Full paper review card returned by Paper Reader / Deep Researcher."""
    relevance_score: float = 0.0  # 0.0 – 1.0
    techniques: list[str] = Field(default_factory=list)
    claims: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    key_results: list[str] = Field(default_factory=list)
    review_pass: int = 1  # 1, 2, or 3 (Karpathy model)
    code_url: Optional[str] = None
    critique: Optional[str] = None


class ResearchQuery(BaseModel):
    """Input for any research pipeline."""
    goal: str
    primary_url: Optional[str] = None
    secondary_url: Optional[str] = None
    seed_arxiv_id: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    mode: ResearchMode = ResearchMode.DEEP


# ---------------------------------------------------------------------------
# Environment Config
# ---------------------------------------------------------------------------

class Settings(BaseModel):
    """Runtime configuration loaded from environment."""
    # AWS Settings (for Amazon Nova via Bedrock)
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")

    # Optional provider APIs.
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    openalex_email: str = Field(default_factory=lambda: os.getenv("OPENALEX_EMAIL", ""))
    openalex_api_key: str = Field(default_factory=lambda: os.getenv("OPENALEX_API_KEY", ""))
    kernel_api_key: str = Field(default_factory=lambda: os.getenv("KERNEL_API_KEY", ""))
    tinyfish_api_key: str = Field(default_factory=lambda: os.getenv("TINYFISH_API_KEY", ""))


settings = Settings()
