from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..contracts import SearchResult


class SearchProvider(ABC):
    """
    Abstract base class for search providers.
    """
    
    @abstractmethod
    async def search(self, query: str, max_results: int, include_domains: List[str] = None, 
                     exclude_domains: List[str] = None) -> List[SearchResult]:
        """
        Perform a search and return normalized results.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            include_domains: Domains to prioritize
            exclude_domains: Domains to exclude
            
        Returns:
            List of SearchResult objects
        """
        pass