from typing import List, Optional
from urllib.parse import urlparse
from ..contracts import SearchResult
import time
from datetime import datetime


def get_domain(url: str) -> str:
    """
    Extract domain from URL.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.hostname or ""
        # Remove www prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower()
    except Exception:
        return ""


def rank(results: List[SearchResult], include_domains: Optional[List[str]] = None,
         exclude_domains: Optional[List[str]] = None, max_results: int = 6) -> List[SearchResult]:
    """
    Rank and deduplicate search results.
    
    Args:
        results: List of search results to rank
        include_domains: Domains to boost
        exclude_domains: Domains to exclude
        max_results: Maximum number of results to return
        
    Returns:
        Ranked and filtered list of results
    """
    # Normalize domain lists
    include_set = set()
    exclude_set = set()
    
    if include_domains:
        include_set = {domain.lower() for domain in include_domains}
    
    if exclude_domains:
        exclude_set = {domain.lower() for domain in exclude_domains}
    
    # Filter out excluded domains
    filtered_results = []
    for result in results:
        domain = get_domain(result.url)
        if domain in exclude_set:
            continue
        filtered_results.append(result)
    
    # Boost included domains
    for result in filtered_results:
        domain = get_domain(result.url)
        if include_set and domain in include_set:
            result.score += 0.25
    
    # Deduplicate by URL path
    seen_paths = set()
    deduped_results = []
    for result in filtered_results:
        try:
            parsed = urlparse(result.url)
            path_key = f"{get_domain(result.url)}|{parsed.path}"
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                deduped_results.append(result)
        except Exception:
            # If we can't parse the URL, just include it
            deduped_results.append(result)
    
    # Apply recency boost
    for result in deduped_results:
        if result.published:
            try:
                # Parse the published date
                pub_date = datetime.fromisoformat(result.published.replace('Z', '+00:00'))
                age_days = (datetime.now(pub_date.tzinfo) - pub_date).days
                # Normalize age to 0-365 days
                age_days = min(365, max(0, age_days))
                # Apply recency boost (newer = higher score)
                recency_boost = (1 - age_days/365) * 0.2
                result.score += recency_boost
            except Exception:
                # If we can't parse the date, no boost
                pass
    
    # Sort by score (descending)
    deduped_results.sort(key=lambda x: x.score, reverse=True)
    
    # Return top results
    return deduped_results[:max_results]