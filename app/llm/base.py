"""Common interface for vision-language model backends.

Ollama (self-hosted) and Bedrock (managed, Week 5) both implement this,
so the API code never changes when you switch backends.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VLMAnswer:
    text: str
    model: str
    latency_s: float


class VLMBackend(ABC):
    @abstractmethod
    async def ask(self, question: str, images: list[bytes]) -> VLMAnswer:
        """Answer a question about zero or more images."""

    @abstractmethod
    async def health(self) -> bool:
        """Return True if the backend is reachable."""
