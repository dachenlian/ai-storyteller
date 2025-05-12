from pathlib import Path
from typing import Protocol


class MusicGenerationModel(Protocol):
    def generate_music(self, prompt: str) -> Path | None:
        """Generates music based on the provided prompt. Returns the path to the generated music file or None if generation fails."""
        ...
