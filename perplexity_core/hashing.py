import hashlib
import json
from typing import Dict, Any
from .contracts import SearchRequest


def query_key(req: SearchRequest) -> str:
    """
    Generate a cache key for a search request.
    """
    # Create a dictionary with only the fields that affect the search results
    key_data = {
        "query": req.query,
        "maxResults": req.maxResults,
        "locale": req.locale,
        "timeRange": req.timeRange,
        "includeDomains": sorted(req.includeDomains) if req.includeDomains else [],
        "excludeDomains": sorted(req.excludeDomains) if req.excludeDomains else [],
    }
    
    # Convert to JSON string and hash it
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()


def url_key(url: str) -> str:
    """
    Generate a cache key for a URL.
    """
    return hashlib.sha256(url.encode('utf-8')).hexdigest()