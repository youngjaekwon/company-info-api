from fastapi import FastAPI

from app.containers.main_container import AppContainer


def create_app() -> FastAPI:
    container = AppContainer()

    app = FastAPI(
        title="Company Info API",
        version="1.0.0",
    )

    app.container = container

    return app

app = create_app()
