from typing import Dict, Any


def apply_safety_guard(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply safety guard to the response.
    """
    # Check if topic is medical/legal/financial and add disclaimer
    query = response.get("query", "")
    answer = response.get("answer", "")
    
    sensitive_topics = ['medical', 'legal', 'financial', 'health', 'law', 'finance', 'medicine', 'doctor', 'lawyer', 'investment']
    is_sensitive = any(topic in query.lower() or topic in answer.lower() for topic in sensitive_topics)
    
    if is_sensitive:
        response["answer"] += " Note: This is not professional advice."
    
    return response