from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import time
import asyncio
import json

from perplexity_core.contracts import DiscoverRequest, DiscoverResponse, DiscoverRecommendation, Diagnostics
from perplexity_core.config import settings
from perplexity_core.search.tavily import TavilySearchProvider
from perplexity_core.search.brave import BraveSearchProvider
from perplexity_core.search.searchapi import SearchApiProvider
from perplexity_core.extract.firecrawl import FirecrawlExtractor
from perplexity_core.extract.readability import ReadabilityExtractor
from perplexity_core.llm.openrouter import OpenRouterProvider
from perplexity_core.llm.ollama import OllamaProvider
from perplexity_core.rank.ranker import rank

router = APIRouter(prefix="/api/discover", tags=["discover"])


# Planning prompt for discovering sources
DISCOVER_PLANNING_SYSTEM = """You are a research planning expert. Given a high-level topic, plan specific search queries
that would help find the most relevant and authoritative sources. Return STRICT JSON matching the provided schema."""

DISCOVER_PLANNING_USER = """Schema:
{{
  "type": "object",
  "required": ["queries"],
  "properties": {{
    "queries": {{
      "type": "array",
      "items": {{"type": "string"}},
      "maxItems": 5
    }}
  }}
}}

Topic:
"{topic}"

Instructions:
- Plan 3-5 specific search queries
- Focus on authoritative, recent sources
- Vary query types (definitions, recent developments, expert opinions, etc.)
- Output strict JSON only"""


async def plan_search_queries(topic: str, provider) -> List[str]:
    """
    Plan optimized search queries for a given topic.
    """
    user_prompt = DISCOVER_PLANNING_USER.format(topic=topic)
    
    try:
        response = await provider.chat(
            DISCOVER_PLANNING_SYSTEM,
            user_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse JSON response
        import json
        parsed = json.loads(response)
        return parsed.get("queries", [])
    except Exception as e:
        print(f"Failed to plan search queries: {e}")
        # Fallback to simple query
        return [topic]


async def search_sources(queries: List[str], max_sources: int, time_range: str) -> List[Dict[str, Any]]:
    """
    Search for sources using the configured search providers.
    """
    all_results = []
    
    for query in queries:
        # Try Brave first
        try:
            provider = BraveSearchProvider()
            results = await provider.search(query, max_sources // len(queries))
            all_results.extend([r.model_dump() for r in results])
            continue
        except Exception as e:
            print(f"Brave search failed for query '{query}': {e}")
        
        # Fallback to Tavily
        try:
            provider = TavilySearchProvider()
            results = await provider.search(query, max_sources // len(queries))
            all_results.extend([r.model_dump() for r in results])
            continue
        except Exception as e:
            print(f"Tavily search failed for query '{query}': {e}")
        
        # Fallback to SearchAPI
        try:
            provider = SearchApiProvider()
            results = await provider.search(query, max_sources // len(queries))
            all_results.extend([r.model_dump() for r in results])
        except Exception as e:
            print(f"SearchAPI search failed for query '{query}': {e}")
    
    return all_results


async def extract_content(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Extract content from URLs using Firecrawl or Readability.
    """
    # Try Firecrawl first
    try:
        extractor = FirecrawlExtractor()
        extracted = await extractor.extract_many(urls)
        return extracted
    except Exception as e:
        print(f"Firecrawl extraction failed: {e}")
    
    # Fallback to Readability
    try:
        extractor = ReadabilityExtractor()
        extracted = await extractor.extract_many(urls)
        return extracted
    except Exception as e:
        print(f"Readability extraction failed: {e}")
    
    return []


async def curate_recommendations(extracted_docs, provider) -> List[Dict[str, Any]]:
    """
    Curate recommendations with why_md and summary_md using LLM.
    """
    if not extracted_docs:
        return []
    
    # Deduplicate by URL
    unique_docs = []
    seen_urls = set()
    for doc in extracted_docs:
        if doc["url"] not in seen_urls:
            unique_docs.append(doc)
            seen_urls.add(doc["url"])
    
    # Limit to 10 docs
    unique_docs = unique_docs[:10]
    
    # Create curation prompt
    CURATION_SYSTEM = """You are a research curation expert. Given extracted documents, create concise recommendations
with explanations of why each source is valuable. Return STRICT JSON matching the provided schema."""

    CURATION_USER = f"""Schema:
{{
  "type": "object",
  "required": ["recommendations"],
  "properties": {{
    "recommendations": {{
      "type": "array",
      "items": {{
        "type": "object",
        "required": ["title", "url", "why_md", "summary_md"],
        "properties": {{
          "title": {{"type": "string"}},
          "url": {{"type": "string"}},
          "why_md": {{"type": "string"}},
          "summary_md": {{"type": "string"}},
          "published": {{"type": "string"}},
          "score": {{"type": "number"}}
        }}
      }},
      "maxItems": 10
    }}
  }}
}}

Documents:
{json.dumps(unique_docs, indent=2, ensure_ascii=False)}

Instructions:
- Create up to 10 recommendations
- For each, write a brief "why" explanation in markdown
- Write a 2-4 sentence annotated summary in markdown
- Include publication date if available
- Assign relevance scores (0.0-1.0)
- Output strict JSON only"""
    
    try:
        response = await provider.chat(
            CURATION_SYSTEM,
            CURATION_USER,
            temperature=0.2,
            max_tokens=2000
        )
        
        # Parse JSON response
        parsed = json.loads(response)
        return parsed.get("recommendations", [])
    except Exception as e:
        print(f"Failed to curate recommendations: {e}")
        # Fallback to simple recommendations
        recommendations = []
        for doc in unique_docs[:10]:
            recommendations.append({
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "why_md": "Relevant source for the topic",
                "summary_md": doc.get("text", "")[:200] + "..." if len(doc.get("text", "")) > 200 else doc.get("text", ""),
                "published": doc.get("published", None),
                "score": 0.5
            })
        return recommendations


@router.post("", response_model=DiscoverResponse)
async def discover_sources(req: DiscoverRequest):
    """
    Discover and curate sources for a given topic.
    """
    if not settings.DISCOVER_ENABLED:
        raise HTTPException(status_code=400, detail="Discover feature is disabled")
    
    start_time = time.time()
    
    try:
        # Select LLM provider (default to OpenRouter)
        if settings.OPENROUTER_API_KEY:
            provider = OpenRouterProvider()
        else:
            provider = OllamaProvider()
        
        # 1. Plan search queries
        print(f"Planning search queries for topic: {req.topic}")
        queries_planned = await plan_search_queries(req.topic, provider)
        print(f"Planned queries: {queries_planned}")
        
        # 2. Search for sources
        print("Searching for sources...")
        search_results = await search_sources(queries_planned, req.maxSources, req.timeRange)
        print(f"Found {len(search_results)} search results")
        
        # 3. Extract content
        print("Extracting content...")
        urls = [result["url"] for result in search_results]
        extracted_docs = await extract_content(urls)
        print(f"Extracted content from {len(extracted_docs)} sources")
        
        # 4. Curate recommendations
        print("Curating recommendations...")
        curated_recommendations = await curate_recommendations(extracted_docs, provider)
        print(f"Curated {len(curated_recommendations)} recommendations")
        
        # 5. Create diagnostics
        diagnostics = Diagnostics(
            searchProvider="brave",  # Default for now
            llm=settings.OPENROUTER_MODEL if settings.OPENROUTER_API_KEY else settings.OLLAMA_MODEL,
            latencyMs=int((time.time() - start_time) * 1000),
            cached=False
        )
        
        # 6. Create response
        response = DiscoverResponse(
            recommendations=[DiscoverRecommendation(**rec) for rec in curated_recommendations],
            queries_planned=queries_planned,
            diagnostics=diagnostics
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discover pipeline error: {str(e)}")