"""包管理 API 端点"""

from fastapi import APIRouter, HTTPException, Query

from pipview.core.pip_service import package_service
from pipview.core.schemas import (
    InstallRequest,
    PackageInfo,
    TaskResponse,
    UninstallRequest,
    UpgradeRequest,
)

router = APIRouter()


@router.get("/list")
async def list_packages(
    search: str = Query(None),
):
    """获取已安装包列表"""
    result = package_service.list_packages(search=search)
    result["packages"] = [PackageInfo(**pkg) for pkg in result["packages"]]
    return result


@router.get("/info/{package_name}")
async def get_package_info(package_name: str):
    """获取包详细信息"""
    info = package_service.get_package_info(package_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")
    return info


@router.get("/search")
async def search_packages(q: str = Query(..., min_length=1)):
    """搜索包"""
    results = package_service.search_packages(q)
    return {"total": len(results), "results": results}


@router.post("/install", response_model=TaskResponse)
async def install_package(request: InstallRequest):
    """安装包"""
    success, output = await package_service.install_package(
        package_name=request.package_name,
        version=request.version,
        upgrade=request.upgrade,
        extra_args=request.extra_args,
    )

    return TaskResponse(
        task_id="install",
        status="success" if success else "failed",
        message="Package installed successfully" if success else "Installation failed",
        output=output,
    )


@router.post("/uninstall", response_model=TaskResponse)
async def uninstall_package(request: UninstallRequest):
    """卸载包"""
    success, output = await package_service.uninstall_package(
        package_name=request.package_name,
        force=request.force,
    )

    return TaskResponse(
        task_id="uninstall",
        status="success" if success else "failed",
        message="Package uninstalled successfully" if success else "Uninstallation failed",
        output=output,
    )


@router.post("/upgrade", response_model=TaskResponse)
async def upgrade_package(request: UpgradeRequest):
    """升级包"""
    if request.all:
        success, output = await package_service.upgrade_all()
        return TaskResponse(
            task_id="upgrade_all",
            status="success" if success else "failed",
            message="All packages upgraded successfully" if success else "Upgrade failed",
            output=output,
        )

    if not request.package_name:
        raise HTTPException(status_code=400, detail="package_name is required when 'all' is false")

    success, output = await package_service.upgrade_package(request.package_name)

    return TaskResponse(
        task_id=f"upgrade_{request.package_name}",
        status="success" if success else "failed",
        message=f"Package '{request.package_name}' upgraded successfully" if success else "Upgrade failed",
        output=output,
    )


@router.get("/versions/{package_name}")
async def get_package_versions(package_name: str):
    """获取包所有可用版本"""
    versions = await package_service.get_package_versions(package_name)
    return {"versions": versions}


@router.post("/downgrade", response_model=TaskResponse)
async def downgrade_package(request: UpgradeRequest):
    """降级包"""
    if not request.package_name:
        raise HTTPException(status_code=400, detail="package_name is required")
    if not request.version:
        raise HTTPException(status_code=400, detail="version is required for downgrade")

    success, output = await package_service.downgrade_package(request.package_name, request.version)

    return TaskResponse(
        task_id=f"downgrade_{request.package_name}",
        status="success" if success else "failed",
        message=f"Package '{request.package_name}' downgraded to {request.version}" if success else "Downgrade failed",
        output=output,
    )


@router.get("/check-updates")
async def check_updates():
    """检查可升级的包"""
    result = package_service.list_packages(page=1, page_size=50)
    updatable = []

    for pkg in result["packages"]:
        results = package_service.search_packages(pkg["name"])
        if results:
            latest = results[0].get("version")
            if latest and latest != pkg.get("version"):
                updatable.append(
                    {
                        "name": pkg["name"],
                        "current_version": pkg.get("version"),
                        "latest_version": latest,
                    }
                )

    return {"total": len(updatable), "packages": updatable}


@router.get("/check-conflicts")
async def check_conflicts():
    """检查包冲突"""
    result = await package_service.check_conflicts()
    return result
