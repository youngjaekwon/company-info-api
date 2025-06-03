from fastapi import FastAPI

from app.api.v1.route import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Info API",
        version="1.0.0",
    )

    app.include_router(v1_router)

    return app


app = create_app()
