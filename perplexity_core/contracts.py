from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from typing import Literal


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
    selectedModel: Optional[str] = None
    selectedProvider: Optional[str] = None
    # Structured content generation
    output_type: Literal["answer", "faq", "study_guide", "briefing_doc", "timeline", "mind_map"] | None = None


# Structured content schemas
class FAQItem(BaseModel):
    q: str
    a_md: str


class FAQPayload(BaseModel):
    type: str = "faq"
    version: str = "1.0"
    items: List[FAQItem]


class StudyGuideQuizItem(BaseModel):
    question: str
    answer_md: str


class StudyGuideGlossaryItem(BaseModel):
    term: str
    def_md: str


class StudyGuideModule(BaseModel):
    title: str
    notes_md: str
    quiz: List[StudyGuideQuizItem]
    glossary: List[StudyGuideGlossaryItem]


class StudyGuidePayload(BaseModel):
    type: str = "study_guide"
    version: str = "1.0"
    modules: List[StudyGuideModule]


class BriefingSection(BaseModel):
    heading: str
    content_md: Optional[str] = None
    items: Optional[List[str]] = None


class BriefingPayload(BaseModel):
    type: str = "briefing_doc"
    version: str = "1.0"
    sections: List[BriefingSection]


class TimelineEvent(BaseModel):
    date: str
    title: str
    summary_md: str
    source_urls: List[str]


class TimelinePayload(BaseModel):
    type: str = "timeline"
    version: str = "1.0"
    events: List[TimelineEvent]


class MindMapNode(BaseModel):
    id: str
    label: str
    children: List["MindMapNode"] = []


class MindMapPayload(BaseModel):
    type: str = "mind_map"
    version: str = "1.0"
    nodes: List[MindMapNode]


# Update forward references
MindMapNode.model_rebuild()


class StructuredPayload(BaseModel):
    # Union of all structured content types
    pass


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
    # Structured content generation
    structured: Optional[Dict[str, Any]] = None


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


# Discover Sources request and response
class DiscoverRequest(BaseModel):
    topic: str
    maxSources: int = Field(default=10, ge=1, le=20)
    timeRange: str = "365d"
    locale: str = "en"


class DiscoverRecommendation(BaseModel):
    title: str
    url: str
    why_md: str
    summary_md: str
    published: Optional[str] = None
    score: float = 0.0


class DiscoverResponse(BaseModel):
    recommendations: List[DiscoverRecommendation]
    queries_planned: List[str]
    diagnostics: Diagnostics