from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass
class ChatMessage:
    role: str
    content: str


class TextGenerationModel(Protocol):
    def generate_text(self, prompt: str | Sequence[ChatMessage]) -> str:
        """Generates text based on the provided prompt. Returns the generated text."""
        ...