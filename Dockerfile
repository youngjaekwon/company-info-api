FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV APP_ENV=prod

COPY . /src
WORKDIR /src

RUN uv sync --frozen

EXPOSE 8000

RUN chmod +x /src/entrypoint.sh
ENTRYPOINT ["/src/entrypoint.sh"]

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]