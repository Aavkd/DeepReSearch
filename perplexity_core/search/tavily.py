import httpx
from typing import List, Optional
from .base import SearchProvider
from ..contracts import SearchResult
from ..config import settings


class TavilySearchProvider(SearchProvider):
    """
    Tavily search provider implementation.
    """
    
    async def search(self, query: str, max_results: int, include_domains: List[str] = None,
                     exclude_domains: List[str] = None) -> List[SearchResult]:
        """
        Perform a search using the Tavily API.
        """
        if not settings.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not configured")
        
        url = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
            "include_domains": include_domains or [],
            "exclude_domains": exclude_domains or []
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append(SearchResult(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    snippet=item.get("snippet", ""),
                    score=item.get("score", 0.5),
                    published=item.get("published")
                ))
            
            return results