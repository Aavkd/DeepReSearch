import json
import httpx
from typing import Optional
from .base import LLMProvider
from ..config import settings


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider implementation.
    """
    
    def __init__(self, model: Optional[str] = None):
        self.host = settings.OLLAMA_HOST
        self.model = model or settings.OLLAMA_MODEL
    
    async def chat(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Send a chat message to Ollama.
        """
        url = f"{self.host}/api/chat"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Default parameters
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "options": {
                "temperature": kwargs.get("temperature", 0.2),
                "num_predict": kwargs.get("num_predict", -1)  # Allow full response
            },
            "stream": False  # Ensure we get complete response
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature", "num_predict"]:
                payload[key] = value
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Validate response structure
                if "message" not in data:
                    raise ValueError(f"Invalid Ollama response structure: {data}")
                
                if "content" not in data["message"]:
                    raise ValueError(f"Missing content in Ollama response: {data}")
                
                content = data["message"]["content"]
                
                # Basic validation of content
                if not content or not isinstance(content, str):
                    raise ValueError(f"Invalid content from Ollama: {content}")
                
                return content.strip()
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise Exception("Ollama request timed out")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Ollama response as JSON: {e}")
        except Exception as e:
            raise Exception(f"Ollama request failed: {str(e)}")