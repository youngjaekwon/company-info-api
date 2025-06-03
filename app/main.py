from fastapi import FastAPI

from app.api.v1.route import router as v1_router
from app.containers.main_container import AppContainer


def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Info API",
        version="1.0.0",
    )

    container = AppContainer()
    container.wire(modules=["app.api.v1.company", "app.api.v1.admin"])

    app.container = container

    app.include_router(v1_router)

    return app


app = create_app()
