import httpx
from typing import List, Optional
from urllib.parse import urlencode
from .base import SearchProvider
from ..contracts import SearchResult
from ..config import settings


class SearchApiProvider(SearchProvider):
    """
    SearchAPI.io provider implementation (Google search).
    """
    
    async def search(self, query: str, max_results: int, include_domains: List[str] = None,
                     exclude_domains: List[str] = None) -> List[SearchResult]:
        """
        Perform a search using SearchAPI.io.
        """
        if not settings.SEARCHAPI_IO_KEY:
            raise ValueError("SEARCHAPI_IO_KEY is not configured")
        
        # Build query parameters
        params = {
            "engine": "google",
            "q": query,
            "api_key": settings.SEARCHAPI_IO_KEY
        }
        
        url = f"https://www.searchapi.io/api/v1/search?{urlencode(params)}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            results = []
            organic_results = data.get("organic_results", [])
            for item in organic_results[:max_results]:
                results.append(SearchResult(
                    url=item.get("link", ""),
                    title=item.get("title", ""),
                    snippet=item.get("snippet", ""),
                    score=0.5,  # SearchAPI doesn't provide a score, so we use default
                    published=None  # SearchAPI doesn't provide publication date
                ))
            
            return results