from typing import Dict, Any


def apply_safety_guard(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply safety guard to the response.
    """
    # Check if topic is medical/legal/financial and add disclaimer
    query = response.get("query", "")
    answer = response.get("answer", "")
    
    # Check structured content if present
    structured = response.get("structured", {})
    structured_text = ""
    if structured:
        # Extract text from structured content for safety checking
        if structured.get("type") == "faq":
            for item in structured.get("items", []):
                structured_text += item.get("q", "") + " " + item.get("a_md", "") + " "
        elif structured.get("type") == "study_guide":
            for module in structured.get("modules", []):
                structured_text += module.get("title", "") + " " + module.get("notes_md", "") + " "
                for quiz in module.get("quiz", []):
                    structured_text += quiz.get("question", "") + " " + quiz.get("answer_md", "") + " "
                for glossary in module.get("glossary", []):
                    structured_text += glossary.get("term", "") + " " + glossary.get("def_md", "") + " "
        elif structured.get("type") == "briefing_doc":
            for section in structured.get("sections", []):
                structured_text += section.get("heading", "") + " " + (section.get("content_md", "") or "") + " "
                for item in section.get("items", []):
                    structured_text += item + " "
        elif structured.get("type") == "timeline":
            for event in structured.get("events", []):
                structured_text += event.get("title", "") + " " + event.get("summary_md", "") + " "
        elif structured.get("type") == "mind_map":
            def extract_node_text(node):
                text = node.get("label", "") + " "
                for child in node.get("children", []):
                    text += extract_node_text(child)
                return text
            for node in structured.get("nodes", []):
                structured_text += extract_node_text(node)
    
    sensitive_topics = ['medical', 'legal', 'financial', 'health', 'law', 'finance', 'medicine', 'doctor', 'lawyer', 'investment']
    is_sensitive = any(topic in query.lower() or topic in answer.lower() or topic in structured_text.lower() for topic in sensitive_topics)
    
    if is_sensitive:
        response["answer"] += " Note: This is not professional advice."
    
    return response