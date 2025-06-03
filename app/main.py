from fastapi import FastAPI

from app.containers.main_container import AppContainer
from app.api.v1.route import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Info API",
        version="1.0.0",
    )

    container = AppContainer()
    container.wire(modules=["app.api.v1.company"])

    app.container = container

    app.include_router(v1_router)

    return app


app = create_app()
