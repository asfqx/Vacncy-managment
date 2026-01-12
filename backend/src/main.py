from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield

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
