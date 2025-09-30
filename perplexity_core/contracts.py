from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UIOptions(BaseModel):
    mode: str = "concise"  # or "detailed"


class SearchRequest(BaseModel):
    query: str
    maxResults: int = Field(default=6, ge=3, le=12)
    locale: str = "en"
    timeRange: str = "30d"
    strict: bool = True
    forceLocal: bool = False
    includeDomains: Optional[List[str]] = None
    excludeDomains: Optional[List[str]] = None
    ui: UIOptions = Field(default_factory=UIOptions)


class Source(BaseModel):
    title: str
    url: str
    published: Optional[str] = None
    snippet: str
    relevance: float


class Diagnostics(BaseModel):
    searchProvider: Optional[str] = None
    llm: Optional[str] = None
    latencyMs: Optional[int] = None
    cached: bool = False
    tokens: Optional[Dict[str, int]] = None
    notes: Optional[str] = None


class SearchResponse(BaseModel):
    answer: str
    bullets: List[str]
    sources: List[Source]
    diagnostics: Diagnostics


class SearchResult(BaseModel):
    url: str
    title: str = ""
    snippet: str = ""
    score: float = 0.5
    published: Optional[str] = None


class InternalRecord(BaseModel):
    id: Optional[int] = None
    query: str
    normalized_query: Optional[str] = None
    params_json: Dict[str, Any]
    sources_json: List[Dict[str, Any]]
    answer_json: Dict[str, Any]
    created_at: Optional[datetime] = None