from typing import Optional, AsyncIterator
from .base import AIProvider
from openai import OpenAI, AsyncOpenAI
import logging

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logging.info(f"Initialized OpenAI provider with model {model}")

    async def complete(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      **kwargs) -> str:
        """Generate a completion using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI completion error: {e}")
            raise

    async def stream(self, 
                    prompt: str, 
                    system_prompt: Optional[str] = None,
                    **kwargs) -> AsyncIterator[str]:
        """Stream a completion from OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logging.error(f"OpenAI streaming error: {e}")
            raise

    def get_token_count(self, text: str) -> int:
        """Get approximate token count."""
        # Simple approximation - OpenAI suggests ~4 chars per token
        return len(text) // 4