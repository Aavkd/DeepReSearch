import httpx
import asyncio
from typing import List, Dict, Any, Optional
from ..config import settings
from ..util.text import clean_text


class FirecrawlExtractor:
    """
    Firecrawl extraction implementation.
    """
    
    def __init__(self):
        if not settings.FIRECRAWL_API_KEY:
            raise ValueError("FIRECRAWL_API_KEY is not configured")
        self.api_key = settings.FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v1"
    
    async def extract(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a URL using Firecrawl.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Simplified payload based on what we know works
        payload = {
            "url": url
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/scrape",
                    json=payload,
                    headers=headers,
                    timeout=settings.REQUEST_TIMEOUT_S
                )
                response.raise_for_status()
                data = response.json()
                
                # Handle the response format correctly
                if data.get("success"):
                    result_data = data.get("data", {})
                    result = {
                        "url": url,
                        "title": result_data.get("metadata", {}).get("title", ""),
                        "markdown": clean_text(result_data.get("markdown", "")),
                        "text": clean_text(result_data.get("text", result_data.get("markdown", ""))),
                        "published": result_data.get("metadata", {}).get("published")
                    }
                    return result
                else:
                    error_message = data.get("error", "Unknown error")
                    print(f"Firecrawl API error for {url}: {error_message}")
                    return None
                    
            except httpx.HTTPStatusError as e:
                print(f"HTTP error extracting content from {url}: {e.response.status_code} - {e.response.text}")
                return None
            except Exception as e:
                print(f"Error extracting content from {url}: {e}")
                return None
    
    async def extract_many(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extract content from multiple URLs concurrently.
        """
        semaphore = asyncio.Semaphore(min(settings.MAX_CONCURRENCY, 3))  # Limit concurrency further
        
        async def extract_with_semaphore(url):
            async with semaphore:
                return await self.extract(url)
        
        tasks = [extract_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None values and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result is not None:
                valid_results.append(result)
            elif isinstance(result, Exception):
                print(f"Extraction failed: {result}")
        
        return valid_results