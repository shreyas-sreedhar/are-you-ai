"""RUAI backend entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import APP_DESCRIPTION, APP_NAME, APP_VERSION, settings
from services.nim_client import nim_client

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ruai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not the bound address: uvicorn's own --host/--port win over these, and
    # printing settings.port next to a server started with --port 8001 is how
    # people lose twenty minutes.
    logger.info("%s %s starting", APP_NAME, APP_VERSION)
    logger.info("vision model: %s", settings.nim_vision_model)
    logger.info("text model:   %s", settings.nim_text_model)

    if not settings.nim_configured:
        logger.warning(
            "NIM_API_KEY is not set. Video and article checks will return 503; "
            "message checks will fall back to the local pattern scan. "
            "Copy .env.example to .env and add a key from build.nvidia.com."
        )

    yield

    # The NIM client holds a pooled connection for the process lifetime.
    await nim_client.aclose()
    logger.info("%s stopped", APP_NAME)


app = FastAPI(
    title=f"{APP_NAME} API",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # Explicit list for anything deployed.
    allow_origins=settings.allowed_origins,
    # Two things a wildcard entry cannot express:
    #  - Chrome sends `Origin: chrome-extension://<32 letters>`.
    #  - Local development moves ports whenever one is already taken, and
    #    losing an afternoon to a CORS error is a bad trade for a service
    #    that is bound to the loopback interface anyway.
    allow_origin_regex=(
        r"^(chrome-extension://[a-p]{32}"
        r"|http://(localhost|127\.0\.0\.1)(:\d{1,5})?)$"
    ),
    # No cookies or auth headers are used, so credentials stay off. This also
    # keeps the browser from rejecting the config outright.
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(router)


@app.get("/", tags=["system"])
async def root() -> dict[str, object]:
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "docs": "/docs",
        "checks": [
            "POST /api/v1/check/video",
            "POST /api/v1/check/message",
            "POST /api/v1/check/article",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
