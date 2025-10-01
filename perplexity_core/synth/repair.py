import json
import re
from typing import Dict, Any
from ..llm.openrouter import OpenRouterProvider
from ..llm.ollama import OllamaProvider
from ..config import settings


async def ensure_json(raw_response: str) -> Dict[str, Any]:
    """
    Ensure the response is valid JSON, attempting to repair if necessary.
    """
    if not raw_response or not raw_response.strip():
        return _get_error_response("Empty response from LLM")
    
    # Clean the response first
    cleaned_response = raw_response.strip()
    
    # First, try to parse as-is
    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"Initial JSON parsing failed: {e}")
    
    # Try to extract JSON from markdown code blocks (multiple patterns)
    json_patterns = [
        r'```(?:json)?\s*({.*?})\s*```',  # Standard markdown
        r'```(?:json)?\s*\n({.*?})\s*```',  # With newline after opening
        r'json\s*({.*?})',  # Just 'json' prefix
        r'```\s*({.*?})\s*```'  # Any code block
    ]
    
    for pattern in json_patterns:
        json_match = re.search(pattern, cleaned_response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON-like content in the response (improved)
    brace_start = cleaned_response.find('{')
    brace_end = cleaned_response.rfind('}')
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        json_str = cleaned_response[brace_start:brace_end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Extracted JSON parsing failed: {e}")
            # Try to fix common JSON issues
            try:
                fixed_json = _fix_common_json_issues(json_str)
                return json.loads(fixed_json)
            except json.JSONDecodeError:
                pass
    
    # Look for multiple JSON objects and take the first complete one
    try:
        return _extract_first_complete_json(cleaned_response)
    except Exception:
        pass
    
    # If all else fails, try to repair with an LLM
    try:
        print("Attempting LLM-based JSON repair...")
        return await repair_with_llm(raw_response)
    except Exception as e:
        print(f"LLM repair failed: {e}")
        # If repair fails, return a basic error structure
        return _get_error_response(f"Failed to parse LLM response: {str(e)[:100]}")


def _fix_common_json_issues(json_str: str) -> str:
    """
    Fix common JSON formatting issues.
    """
    # Remove trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Fix unescaped quotes in strings (basic attempt)
    # This is a simple fix - more complex cases might need the LLM repair
    json_str = re.sub(r'"([^"]*?)"([^,:}\]]*?)"', r'"\1\"\2"', json_str)
    
    return json_str


def _extract_first_complete_json(text: str) -> Dict[str, Any]:
    """
    Try to extract the first complete JSON object from text.
    """
    brace_count = 0
    start_pos = text.find('{')
    if start_pos == -1:
        raise ValueError("No JSON object found")
    
    for i, char in enumerate(text[start_pos:], start_pos):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                json_str = text[start_pos:i+1]
                return json.loads(json_str)
    
    raise ValueError("No complete JSON object found")


def _get_error_response(error_message: str) -> Dict[str, Any]:
    """
    Return a standardized error response structure.
    """
    return {
        "answer": "I apologize, but I encountered an error while processing the response. Please try your query again.",
        "bullets": ["Error occurred during response processing"],
        "sources": [],
        "diagnostics": {
            "notes": error_message
        }
    }


async def repair_with_llm(broken_json: str) -> Dict[str, Any]:
    """
    Use an LLM to repair broken JSON.
    """
    system_prompt = 'You are a JSON repair expert. The user will provide broken JSON. Return the same content as valid JSON only. No explanations.'
    user_prompt = f'Repair this JSON:\n\n{broken_json}'
    
    # Try OpenRouter first, fallback to Ollama
    try:
        provider = OpenRouterProvider()
        repaired = await provider.chat(system_prompt, user_prompt)
        return json.loads(repaired)
    except Exception:
        try:
            provider = OllamaProvider()
            repaired = await provider.chat(system_prompt, user_prompt)
            return json.loads(repaired)
        except Exception:
            # If both fail, re-raise the original exception
            raise ValueError(f"Failed to repair JSON: {broken_json}")