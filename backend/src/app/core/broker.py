from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

import httpx
from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult
from taskiq_aio_pika import AioPikaBroker
import taskiq_fastapi
from taskiq_redis import RedisAsyncResultBackend

from app.core.env import settings


class TaskiqAdminMiddleware(TaskiqMiddleware):

    def __init__(
        self,
        url: str,
        api_token: str,
        taskiq_broker_name: str | None = None,
    ) -> None:

        super().__init__()
        self.url = url
        self.api_token = api_token
        self.__ta_broker_name = taskiq_broker_name

    async def post_send(self, message: TaskiqMessage) -> None:

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()

        async with httpx.AsyncClient() as client:
            await client.post(
                headers={"access-token": self.api_token},
                url=urljoin(self.url, f"/api/tasks/{message.task_id}/queued"),
                json={
                    "args": message.args,
                    "kwargs": message.kwargs,
                    "taskName": message.task_name,
                    "worker": self.__ta_broker_name,
                    "queuedAt": now,
                },
            )
        return super().post_send(message) # pyright: ignore[reportReturnType]

    async def pre_execute(self, message: TaskiqMessage) -> None: # pyright: ignore[reportIncompatibleMethodOverride]

        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        async with httpx.AsyncClient() as client:
            await client.post(
                headers={"access-token": self.api_token},
                url=urljoin(self.url, f"/api/tasks/{message.task_id}/started"),
                json={
                    "startedAt": now,
                    "args": message.args,
                    "kwargs": message.kwargs,
                    "taskName": message.task_name,
                    "worker": self.__ta_broker_name,
                },
            )
        return super().pre_execute(message) # pyright: ignore[reportReturnType]

    async def post_execute(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
    ) -> None:
        now = datetime.now(UTC).replace(tzinfo=None).isoformat()
        async with httpx.AsyncClient() as client:
            await client.post(
                headers={"access-token": self.api_token},
                url=urljoin(
                    self.url,
                    f"/api/tasks/{message.task_id}/executed",
                ),
                json={
                    "finishedAt": now,
                    "error": result.error
                    if result.error is None
                    else repr(result.error),
                    "executionTime": result.execution_time,
                    "returnValue": {"return_value": result.return_value},
                },
            )
        return super().post_execute(message, result) # pyright: ignore[reportReturnType]


broker = (
    AioPikaBroker(settings.rabbitmq_url)
    .with_result_backend(RedisAsyncResultBackend(settings.cache_url))
    .with_middlewares(
        TaskiqAdminMiddleware(
            url="http://taskiq_admin:3000",
            api_token="supersecret",
            taskiq_broker_name="vacancy_broker",
        )
    )
)

taskiq_fastapi.init(broker, "app.main:app")
