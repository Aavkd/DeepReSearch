import httpx
from typing import List, Optional
from urllib.parse import urlencode
from .base import SearchProvider
from ..contracts import SearchResult
from ..config import settings


class BraveSearchProvider(SearchProvider):
    """
    Brave search provider implementation.
    """
    
    async def search(self, query: str, max_results: int, include_domains: List[str] = None,
                     exclude_domains: List[str] = None) -> List[SearchResult]:
        """
        Perform a search using the Brave Search API.
        """
        if not settings.BRAVE_API_KEY:
            raise ValueError("BRAVE_API_KEY is not configured")
        
        # Build query parameters
        params = {
            "q": query,
            "count": min(max_results, 20),  # Brave has a max of 20
        }
        
        if include_domains:
            params["include_domains"] = ",".join(include_domains)
        
        url = f"https://api.search.brave.com/res/v1/web/search?{urlencode(params)}"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": settings.BRAVE_API_KEY
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            web_results = data.get("web", {}).get("results", [])
            for item in web_results:
                results.append(SearchResult(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    snippet=item.get("description", ""),
                    score=0.5,  # Brave doesn't provide a score, so we use default
                    published=None  # Brave doesn't provide publication date
                ))
            
            return results