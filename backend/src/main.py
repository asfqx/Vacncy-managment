from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core import settings, broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    s3_adapter.create_bucket(AVATARS_BUCKET)
    s3_adapter.create_bucket(AI_MODELS)

    if not broker.is_worker_process:    # pyright: ignore

        await broker.startup()      # pyright: ignore
        await create_first_superuser()

        if settings.debug:
            await insert_mock_data()

    yield
    
    if not broker.is_worker_process:     # pyright: ignore
        await broker.shutdown()       # pyright: ignore

app = FastAPI(
    lifespan=lifespan,
    title=settings.app_title,
    description=settings.app_description,
) 

Instrumentator().instrument(app).expose(app, tags=['Metrics'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
