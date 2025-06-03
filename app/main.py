from fastapi import FastAPI

from app.containers.main_container import AppContainer
from app.api.v1.route import router as v1_router


def create_app() -> FastAPI:
    container = AppContainer()

    app = FastAPI(
        title="Company Info API",
        version="1.0.0",
    )

    app.container = container
    container.wire(modules=["app.api.v1.company"])

    app.include_router(v1_router)

    return app


app = create_app()
