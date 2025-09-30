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