import httpx
from typing import Optional
from .base import LLMProvider
from ..config import settings


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter LLM provider implementation.
    """
    
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not configured")
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
    
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
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature", "top_p"]:
                payload[key] = value
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]