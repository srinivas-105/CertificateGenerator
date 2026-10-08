from pathlib import Path

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import Certificate, GenerationJob


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name)
    application.include_router(router, prefix=settings.api_v1_prefix)

    @application.on_event("startup")
    def startup() -> None:
        Base.metadata.create_all(bind=engine)
        Path(settings.output_directory).mkdir(parents=True, exist_ok=True)

    return application


app = create_app()
