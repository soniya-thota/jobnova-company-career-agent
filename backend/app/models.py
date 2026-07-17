from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl

class DiscoverRequest(BaseModel):
    linkedin_url: HttpUrl
    show_browser: bool = False

class DiscoverResult(BaseModel):
    status: str
    company_name: str | None = None
    company_website_url: str | None = None
    career_page_url: str | None = None
    open_position_url: str | None = None
    linkedin_job_title: str | None = None
    linkedin_location: str | None = None
    captured_apply_url: str | None = None
    provider: str = "generic"
    role_match_method: str = "unverified"
    confidence: int = Field(default=0, ge=0, le=100)
    discovery_time_seconds: float = 0.0
    warnings: list[str] = Field(default_factory=list)
