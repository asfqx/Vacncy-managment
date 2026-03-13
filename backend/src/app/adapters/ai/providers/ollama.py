import asyncio
import json
import socket
from typing import Any

import ollama

from app.core.env import settings

from .base import BaseAIProvider


class OllamaProvider(BaseAIProvider):

    def __init__(
        self,
        *,
        echo: bool,
    ) -> None:

        self.model_name = settings.ai_model_name
        self.host_url = settings.ai_model_url
        self.echo = echo

    def _check_connection(self) -> bool:
        try:
            host, port_str = self.host_url.replace("http://", "").split(":")
            port = int(port_str)
            with socket.create_connection((host, port), timeout=1):
                return True

        except Exception:  
            return False

    async def chat(
        self,
        prompt: str,
        data: dict[str, Any],
        temperature: float = 0.1,
    ) -> str:

        loop = asyncio.get_event_loop()

        def sync_chat() -> ollama.ChatResponse:
            
            if not self._check_connection():
                msg = f"Ollama not reachable at {self.host_url}"
                raise ConnectionError(msg)

            client = ollama.Client(host=self.host_url)

            return client.chat(                               # type: ignore reportUnknownMemberType
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            data,
                            ensure_ascii=False,
                            indent=2
                        )
                    },
                ],
                options={"temperature": temperature, "top_p": 0.9},
            )

        response = await loop.run_in_executor(None, sync_chat)
        content = response["message"]["content"].strip()

        return content
