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

router = APIRouter(prefix="/packages", tags=["packages"])


@router.get("")
async def list_packages(
    search: str = Query(None),
):
    """获取已安装包列表"""
    result = package_service.list_packages(search=search)
    result["packages"] = [PackageInfo(**pkg) for pkg in result["packages"]]
    return result


@router.get("/search")
async def search_packages(q: str = Query(..., min_length=1)):
    """搜索包"""
    results = package_service.search_packages(q)
    return {"total": len(results), "results": results}


@router.get("/updates")
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


@router.get("/conflicts")
async def check_conflicts():
    """检查包冲突"""
    result = await package_service.check_conflicts()
    return result


@router.get("/{package_name}")
async def get_package_info(package_name: str):
    """获取包详细信息"""
    info = package_service.get_package_info(package_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")
    return info


@router.get("/{package_name}/versions")
async def get_package_versions(package_name: str):
    """获取包所有可用版本"""
    versions = await package_service.get_package_versions(package_name)
    return {"versions": versions}


@router.post("")
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


@router.delete("/{package_name}")
async def uninstall_package(package_name: str, force: bool = False):
    """卸载包"""
    success, output = await package_service.uninstall_package(
        package_name=package_name,
        force=force,
    )

    return TaskResponse(
        task_id="uninstall",
        status="success" if success else "failed",
        message="Package uninstalled successfully" if success else "Uninstallation failed",
        output=output,
    )


@router.put("/upgrade-all")
async def upgrade_all_packages():
    """升级所有包"""
    success, output = await package_service.upgrade_all()
    return TaskResponse(
        task_id="upgrade_all",
        status="success" if success else "failed",
        message="All packages upgraded successfully" if success else "Upgrade failed",
        output=output,
    )


@router.put("/{package_name}")
async def upgrade_package(package_name: str):
    """升级包"""
    success, output = await package_service.upgrade_package(package_name)

    return TaskResponse(
        task_id=f"upgrade_{package_name}",
        status="success" if success else "failed",
        message=f"Package '{package_name}' upgraded successfully" if success else "Upgrade failed",
        output=output,
    )


@router.put("/{package_name}/version")
async def downgrade_package(package_name: str, version: str):
    """降级包"""
    if not version:
        raise HTTPException(status_code=400, detail="version is required for downgrade")

    success, output = await package_service.downgrade_package(package_name, version)

    return TaskResponse(
        task_id=f"downgrade_{package_name}",
        status="success" if success else "failed",
        message=f"Package '{package_name}' downgraded to {version}" if success else "Downgrade failed",
        output=output,
    )
