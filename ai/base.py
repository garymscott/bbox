from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncIterator

class AIProvider(ABC):
    """Base class for AI service providers."""
    
    @abstractmethod
    async def complete(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      **kwargs) -> str:
        """Generate a completion from the AI service."""
        pass

    @abstractmethod
    async def stream(self, 
                    prompt: str, 
                    system_prompt: Optional[str] = None,
                    **kwargs) -> AsyncIterator[str]:
        """Stream a completion from the AI service."""
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Get the token count for the given text."""
        pass