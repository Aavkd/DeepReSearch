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
    # First, try to parse as-is
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw_response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON-like content in the response
    brace_start = raw_response.find('{')
    brace_end = raw_response.rfind('}')
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        json_str = raw_response[brace_start:brace_end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # If all else fails, try to repair with an LLM
    try:
        return await repair_with_llm(raw_response)
    except Exception:
        # If repair fails, return a basic error structure
        return {
            "answer": "Error processing response",
            "bullets": [],
            "sources": [],
            "diagnostics": {
                "notes": "Failed to parse LLM response"
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