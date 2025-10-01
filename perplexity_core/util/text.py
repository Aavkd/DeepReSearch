import re
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text content.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def clean_query_response(text: Optional[str]) -> str:
    """
    Clean query normalization response, extracting just the query string.
    """
    if not text:
        return ""
    
    # Clean whitespace first
    text = text.strip()
    
    # If response contains multiple lines, try to extract the query
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return ""
    
    # Look for the actual query line (skip explanations, headers, etc.)
    for line in lines:
        # Skip common prefixes that models might add
        if any(line.lower().startswith(prefix) for prefix in [
            'query:', 'search:', 'rewritten:', 'normalized:', 'result:', 
            'here', 'the ', 'answer:', 'response:', '```', 'output:'
        ]):
            # Extract the part after the prefix
            for prefix in ['query:', 'search:', 'rewritten:', 'normalized:', 'result:', 'answer:', 'response:', 'output:']:
                if line.lower().startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
        
        # Skip empty lines or lines that look like explanations
        if (line and 
            not line.startswith('#') and 
            not line.startswith('*') and 
            not line.startswith('-') and 
            not line.lower().startswith('note:') and
            not line.lower().startswith('explanation:') and
            len(line) > 3):  # Avoid very short responses
            return clean_text(line)
    
    # If no good line found, return the first non-empty line
    return clean_text(lines[0]) if lines else ""


def truncate_text(text: str, max_chars: int = 10000) -> str:
    """
    Truncate text to a maximum number of characters.
    """
    if len(text) <= max_chars:
        return text
    
    return text[:max_chars] + '...'


def clean_markdown(markdown: Optional[str]) -> str:
    """
    Clean markdown content.
    """
    if not markdown:
        return ""
    
    # Clean whitespace
    markdown = clean_text(markdown)
    
    # Truncate if too long
    markdown = truncate_text(markdown, 10000)
    
    return markdown