"""Shared contract for inference backends."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    max_new_tokens: int = 1200
    temperature: float = 0.2


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model_id: str
    provider: str


class ModelProvider(Protocol):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text for a bounded request."""
        ...
