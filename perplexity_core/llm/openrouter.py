import httpx
from typing import Optional
from .base import LLMProvider
from ..config import settings


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter LLM provider implementation.
    """
    
    def __init__(self, model: Optional[str] = None):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
    
    async def chat(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Send a chat message to OpenRouter.
        """
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Default parameters
        payload = {
            "model": self.model,
            "temperature": kwargs.get("temperature", 0.2),
            "top_p": kwargs.get("top_p", 0.9),
            "max_tokens": kwargs.get("max_tokens", 4000),  # Reasonable default
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature", "top_p", "max_tokens"]:
                payload[key] = value
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Validate response structure
                if "choices" not in data or not data["choices"]:
                    raise ValueError(f"Invalid OpenRouter response structure: {data}")
                
                if "message" not in data["choices"][0]:
                    raise ValueError(f"Missing message in OpenRouter response: {data}")
                
                if "content" not in data["choices"][0]["message"]:
                    raise ValueError(f"Missing content in OpenRouter response: {data}")
                
                content = data["choices"][0]["message"]["content"]
                
                # Basic validation of content
                if not content or not isinstance(content, str):
                    raise ValueError(f"Invalid content from OpenRouter: {content}")
                
                return content.strip()
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", str(e.response.text))
            except:
                error_detail = str(e.response.text)
            raise Exception(f"OpenRouter HTTP error: {e.response.status_code} - {error_detail}")
        except httpx.TimeoutException:
            raise Exception("OpenRouter request timed out")
        except Exception as e:
            if "OpenRouter" in str(e):
                raise  # Re-raise our custom exceptions
            raise Exception(f"OpenRouter request failed: {str(e)}")