import json
from typing import List, Dict, Any
from ..contracts import SearchRequest


def compose_synthesis_prompt(req: SearchRequest, docs: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Compose the synthesis prompt from the request and documents.
    """
    # Prepare documents for the prompt
    prompt_docs = []
    for doc in docs:
        if doc.get("markdown") or doc.get("text"):
            # Use markdown if available, otherwise text
            excerpt = doc.get("markdown", "") or doc.get("text", "")
            # Limit excerpt length
            excerpt = excerpt[:2000]
            
            prompt_docs.append({
                "url": doc.get("url", ""),
                "title": doc.get("title", ""),
                "excerpt": excerpt
            })
    
    # Convert docs to JSON for the prompt
    docs_json = json.dumps(prompt_docs, ensure_ascii=False)
    
    return {
        "query": req.query,
        "docs_json": docs_json,
        "style_hints": req.ui.mode
    }


def compose_query_normalization_prompt(req: SearchRequest) -> Dict[str, str]:
    """
    Compose the query normalization prompt.
    """
    include_domains = ", ".join(req.includeDomains or [])
    exclude_domains = ", ".join(req.excludeDomains or [])
    
    return {
        "query": req.query,
        "locale": req.locale,
        "time_range": req.timeRange,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains
    }