"""源管理 API 端点"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pipui.core.source_service import source_service
from pipui.core.schemas import SourceInfo, SourceListResponse

router = APIRouter()


class SetSourceRequest(BaseModel):
    """设置源请求"""

    source_url: str
    extra_sources: Optional[list[str]] = None


class AddSourceRequest(BaseModel):
    """添加源请求"""

    name: str
    url: str


class RemoveSourceRequest(BaseModel):
    """移除源请求"""

    url: str


@router.get("/list", response_model=SourceListResponse)
async def list_sources():
    """获取源列表"""
    sources = source_service.get_sources()
    return SourceListResponse(total=len(sources), sources=[SourceInfo(**src) for src in sources])


@router.get("/current")
async def get_current_source():
    """获取当前使用的源"""
    config = source_service.get_pip_config()
    current = config.get("index-url", "https://pypi.org/simple")
    return {"current": current}


@router.post("/set")
async def set_source(request: SetSourceRequest):
    """设置主源"""
    success = source_service.set_source(request.source_url, request.extra_sources)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set source")
    return {"message": "Source updated successfully"}


@router.post("/add")
async def add_source(request: AddSourceRequest):
    """添加额外源"""
    success = source_service.add_source(request.name, request.url)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add source")
    return {"message": "Source added successfully"}


@router.post("/remove")
async def remove_source(request: RemoveSourceRequest):
    """移除额外源"""
    success = source_service.remove_source(request.url)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove source")
    return {"message": "Source removed successfully"}


@router.post("/reset")
async def reset_source():
    """重置为默认源"""
    success = source_service.reset_to_default()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset source")
    return {"message": "Source reset to default"}


@router.get("/defaults")
async def get_default_sources():
    """获取默认源列表"""
    return {
        "sources": [
            {"name": "pypi", "url": "https://pypi.org/simple"},
            {"name": "aliyun", "url": "https://mirrors.aliyun.com/pypi/simple"},
            {"name": "tsinghua", "url": "https://pypi.tuna.tsinghua.edu.cn/simple"},
            {"name": "douban", "url": "https://pypi.doubanio.com/simple"},
        ]
    }
