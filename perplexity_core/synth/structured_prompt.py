import json
from typing import Dict, Any, List
from .templates.structured.faq import FAQ_SYSTEM_PROMPT, FAQ_USER_PROMPT
from .templates.structured.study_guide import STUDY_GUIDE_SYSTEM_PROMPT, STUDY_GUIDE_USER_PROMPT
from .templates.structured.briefing_doc import BRIEFING_DOC_SYSTEM_PROMPT, BRIEFING_DOC_USER_PROMPT
from .templates.structured.timeline import TIMELINE_SYSTEM_PROMPT, TIMELINE_USER_PROMPT
from .templates.structured.mind_map import MIND_MAP_SYSTEM_PROMPT, MIND_MAP_USER_PROMPT


def get_structured_prompts(output_type: str) -> tuple:
    """
    Get the appropriate system and user prompts for the given output type.
    
    Args:
        output_type: The type of structured output to generate
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    prompts = {
        "faq": (FAQ_SYSTEM_PROMPT, FAQ_USER_PROMPT),
        "study_guide": (STUDY_GUIDE_SYSTEM_PROMPT, STUDY_GUIDE_USER_PROMPT),
        "briefing_doc": (BRIEFING_DOC_SYSTEM_PROMPT, BRIEFING_DOC_USER_PROMPT),
        "timeline": (TIMELINE_SYSTEM_PROMPT, TIMELINE_USER_PROMPT),
        "mind_map": (MIND_MAP_SYSTEM_PROMPT, MIND_MAP_USER_PROMPT),
    }
    
    if output_type not in prompts:
        raise ValueError(f"Unsupported output type: {output_type}")
    
    return prompts[output_type]


def compose_structured_prompt(output_type: str, query: str, docs: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Compose a structured prompt for the given output type.
    
    Args:
        output_type: The type of structured output to generate
        query: The user's search query
        docs: List of extracted documents
        
    Returns:
        Dictionary with system_prompt and user_prompt
    """
    system_prompt, user_prompt_template = get_structured_prompts(output_type)
    
    # Convert docs to JSON string for the prompt
    docs_json = json.dumps(docs, indent=2, ensure_ascii=False)
    
    # Format the user prompt with the query and docs
    user_prompt = user_prompt_template.format(
        query=query,
        docs_json=docs_json
    )
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }