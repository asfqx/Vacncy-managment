from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth import auth_router
from app.users import create_first_superuser, users_router
from app.adapters.s3 import s3_adapter
from app.core import settings, AsyncSessionLocal
from app.constant import AVATARS_BUCKET, AI_MODELS
from app.vacancy import search_router as vacancy_router
from app.mock import insert_mock_vacancies
from app.company import company_router
from app.resume import resume_router
from app.response import response_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    s3_adapter.create_bucket(AVATARS_BUCKET)
    s3_adapter.create_bucket(AI_MODELS)

    await create_first_superuser()

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(vacancy_router)
    app.include_router(company_router)
    app.include_router(resume_router)
    app.include_router(response_router)

    async with AsyncSessionLocal() as session:
        await insert_mock_vacancies(session)

    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.app_title,
    description=settings.app_description,
)

Instrumentator().instrument(app).expose(app, tags=["Metrics"])

origins = [
    "http://localhost:5173",
    "https://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
