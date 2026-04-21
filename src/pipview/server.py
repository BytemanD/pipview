"""应用主入口"""

import os
import platform
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse, JSONResponse

from pipview.api.v1.router import api_router
from pipview.common.config import CONF
from pipview.common.logger import get_logger, trace_id_var

logger = get_logger()

OPEN_BROWSER = False


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Trace ID 中间件"""

    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        trace_id_var.set(trace_id)

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting PipView application... OPEN_BROWSER={}", OPEN_BROWSER)
    if OPEN_BROWSER and "windows" in platform.system().lower():
        os.system(f"start http://127.0.0.1:{CONF.app.port}")
    yield
    logger.info("Shutting down PipView application...")


app = FastAPI(
    title=CONF.app.name,
    version=CONF.app.version,
    debug=CONF.app.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(TraceIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal server error",
            "detail": str(exc) if CONF.app.debug else None,
        },
    )


app.include_router(api_router, prefix="/api/v1")


static_dir = Path(__file__).parent / "static"
app.mount("/assets", StaticFiles(directory=str(static_dir.joinpath("assets"))), name="assets")


@app.get("/")
async def root():
    """根路径 - 返回前端页面"""
    if static_dir.exists():
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "PipView API", "version": CONF.app.version}


def run(_app: Optional[str] = None, reload=False):
    global OPEN_BROWSER
    import uvicorn

    OPEN_BROWSER = not reload
    uvicorn.run(
        _app or app,
        host=CONF.app.host,
        port=CONF.app.port,
        reload=reload,
    )


if __name__ == "__main__":
    run()
