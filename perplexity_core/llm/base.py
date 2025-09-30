from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    
    @abstractmethod
    async def chat(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Send a chat message to the LLM and return the response.
        
        Args:
            system_prompt: System message
            user_prompt: User message
            **kwargs: Additional parameters for the LLM
            
        Returns:
            LLM response as string
        """
        pass