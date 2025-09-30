import httpx
from typing import Optional
from .base import LLMProvider
from ..config import settings


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider implementation.
    """
    
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
    
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
                "temperature": kwargs.get("temperature", 0.2)
            }
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature"]:
                payload[key] = value
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return data["message"]["content"]