from abc import ABC, abstractmethod
from typing import Any


class BaseAIProvider(ABC):
    @abstractmethod
    def __init__(
        self,
        *,
        echo: bool = False,
    ) -> None: ...

    @abstractmethod
    async def chat(
        self,
        prompt: str,
        data: dict[str, Any],
        temperature: float = 0.2,
        timeout_seconds: float | None = None,
    ) -> str: ...
