"""API v1 路由"""

from fastapi import APIRouter

from pipui.api.v1.endpoints import packages, sources, config

api_router = APIRouter()

api_router.include_router(packages.router, prefix="/packages", tags=["packages"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
