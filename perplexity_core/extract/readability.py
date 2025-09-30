import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from ..util.text import clean_text


class ReadabilityExtractor:
    """
    Fallback extractor using readability-lxml.
    """
    
    async def extract(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract content from a URL using basic HTML parsing.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to get title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Try to get main content
            # Look for common content containers
            content_selectors = [
                'article',
                '[role="main"]',
                'main',
                '.content',
                '.post',
                '.article'
            ]
            
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text(separator=' ', strip=True)
                    break
            
            # If no specific content found, use body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            return {
                "url": url,
                "title": title,
                "markdown": "",  # No markdown in basic extraction
                "text": clean_text(content),
                "published": None  # No publication date in basic extraction
            }
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None
    
    async def extract_many(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extract content from multiple URLs concurrently.
        """
        tasks = [self.extract(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None values and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result is not None:
                valid_results.append(result)
            elif isinstance(result, Exception):
                print(f"Extraction failed: {result}")
        
        return valid_results