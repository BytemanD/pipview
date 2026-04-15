"""HTTP 工具模块"""

import httpx


async def http_get(url: str, timeout: int = 30) -> dict:
    """GET 请求"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()


async def http_post(url: str, data: dict, timeout: int = 30) -> dict:
    """POST 请求"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=data, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
