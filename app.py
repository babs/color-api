#!/usr/bin/env python3
import io
import logging
import os
from contextlib import asynccontextmanager

import blibs
import dotenv
import PIL.Image
import PIL.ImageColor
from asgi_logger.middleware import AccessLoggerMiddleware
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.responses import PlainTextResponse
from fastapi.responses import StreamingResponse

# from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv()

# Configure logging
blibs.init_root_logger()
logger = logging.getLogger(__name__)

COLORS = {
    "blue": "#3232cd",
    "green": "#32cd32",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.envcol = os.environ.get("COLOR", "grey")
        app.state.rgb_col = PIL.ImageColor.getrgb(
            COLORS.get(
                app.state.envcol,
                app.state.envcol,
            )
        )
    except ValueError:
        app.state.envol = "error"
        app.state.rgb_col = PIL.ImageColor.getrgb("grey")
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan,
    middleware=[
        Middleware(
            AccessLoggerMiddleware,  # type: ignore
            format='%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss',  # noqa # type: ignore
        )
    ],
)


@app.get("/api/v1/png")
@app.get("/")
def gen_png(h: int = 32, w: int = 32):
    def gen_color():
        bio = io.BytesIO()
        img = PIL.Image.new(
            "RGB",
            (min(w, 1024), min(h, 1024)),
            app.state.rgb_col,
        )
        img.save(bio, "PNG", optimize=True)
        bio.seek(0)
        yield from bio

    return StreamingResponse(gen_color(), media_type="image/png")


@app.get("/api/v1/text", response_class=PlainTextResponse)
def get_text_color():
    return app.state.envcol


@app.get("/healthz", response_class=PlainTextResponse)
@app.get("/livez", response_class=PlainTextResponse)
@app.get("/readyz", response_class=PlainTextResponse)
@app.get("/__check/ping", response_class=PlainTextResponse)
def check_ping():
    return "PONG"


if __name__ == "__main__":
    import uvicorn

    uviconfig = None
    if os.environ.get("DEV", "") != "":
        logger.info("reload mode")
        uviconfig = uvicorn.Config(
            "app:app",
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8080")),
            reload=True,
        )
    else:
        uviconfig = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "8080")),
        )

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("access").handlers = []

    server = uvicorn.Server(uviconfig)

    try:
        server.run()
    except Exception:  # pylint: disable=broad-except
        logging.exception("Error starting server")
