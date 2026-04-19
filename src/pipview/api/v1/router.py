"""API v1 路由"""

from fastapi import APIRouter

from pipview.api.v1.endpoints import packages, sources, config

api_router = APIRouter()

api_router.include_router(packages.router)
api_router.include_router(sources.router)
api_router.include_router(config.router)
