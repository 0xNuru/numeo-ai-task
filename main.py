from fastapi import FastAPI
from app.routers import router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging


logger = setup_logging()

app = FastAPI(
    app_name=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
