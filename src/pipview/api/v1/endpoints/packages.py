"""包管理 API 端点"""

import sys
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from pipview.common.pip_helper import ensure_pip, get_pip_command
from pipview.core.pip_service import package_service
from pipview.core.schemas import (
    InstallRequest,
    PackageInfo,
    TaskResponse,
)
from pipview.core.task_manager import task_manager

router = APIRouter(prefix="/packages", tags=["packages"])
executor = ThreadPoolExecutor(max_workers=4)


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
async def install_package(request: InstallRequest, background_tasks: BackgroundTasks):
    """安装包"""
    if not ensure_pip():
        raise HTTPException(status_code=500, detail="无法安装 pip，请检查 Python 环境")

    args = get_pip_command("install")

    if request.upgrade:
        args.append("--upgrade")

    if request.version:
        args.append(f"{request.package_name}=={request.version}")
    else:
        args.append(request.package_name)

    if request.extra_args:
        args.extend(request.extra_args.split())

    task = task_manager.create_task(
        name=f"安装 {request.package_name}",
        package_name=request.package_name,
        task_type="install",
    )

    async def run_install():
        await task_manager.run_install_task(
            task_id=task.task_id,
            args=args,
            package_name=request.package_name,
        )
    background_tasks.add_task(run_install)

    return TaskResponse(
        task_id=task.task_id,
        status="pending",
        message=f"任务已创建: {request.package_name}",
        output=None,
    )


@router.delete("/{package_name}")
async def uninstall_package(package_name: str, background_tasks: BackgroundTasks):
    """卸载包"""
    args = [sys.executable, "-m", "pip", "uninstall", "-y", package_name]

    task = task_manager.create_task(
        name=f"卸载 {package_name}",
        package_name=package_name,
        task_type="uninstall",
    )

    async def run_uninstall():
        success, output = await task_manager.run_install_task(
            task_id=task.task_id,
            args=args,
            package_name=package_name,
        )
        return success, output

    background_tasks.add_task(run_uninstall)

    return TaskResponse(
        task_id=task.task_id,
        status="pending",
        message=f"任务已创建: 卸载 {package_name}",
        output=None,
    )


@router.put("/upgrade-all")
async def upgrade_all_packages(background_tasks: BackgroundTasks):
    """升��所有包"""
    args = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]

    task = task_manager.create_task(
        name="升级所有包",
        task_type="upgrade_all",
    )

    async def run_upgrade_all():
        import subprocess
        task_manager.update_task(task.task_id, status="running", started_at=task.started_at, progress=0)
        task_manager.append_output(task.task_id, "检查可升级的包...\n")

        try:
            p = subprocess.run(args, capture_output=True, text=True)
            if p.returncode != 0:
                task_manager.complete_task(task.task_id, "failed", error="检查可升级包失败")
                return False, "检查可升级包失败"

            import json
            try:
                outdated = json.loads(p.stdout)
            except json.JSONDecodeError:
                task_manager.complete_task(task.task_id, "failed", error="解析包列表失败")
                return False, "解析包列表失败"

            if not outdated:
                task_manager.complete_task(task.task_id, "success", result={"packages": []})
                task_manager.append_output(task.task_id, "没有需要升级的包\n")
                return True, "没有需要升级的包"

            package_names = [pkg["name"] for pkg in outdated]
            task_manager.append_output(task.task_id, f"发现 {len(package_names)} 个包可升级\n")

            upgrade_args = [sys.executable, "-m", "pip", "install", "--upgrade"] + package_names
            success, output = await task_manager.run_install_task(
                task_id=task.task_id,
                args=upgrade_args,
                package_name=", ".join(package_names),
            )
            return success, output
        except Exception as e:
            task_manager.complete_task(task.task_id, "failed", error=str(e))
            return False, str(e)

    background_tasks.add_task(run_upgrade_all)

    return TaskResponse(
        task_id=task.task_id,
        status="pending",
        message="任务已创建: 升级所有包",
        output=None,
    )


@router.put("/{package_name}")
async def upgrade_package(package_name: str, background_tasks: BackgroundTasks):
    """升级包"""
    args = [sys.executable, "-m", "pip", "install", "--upgrade", package_name]

    task = task_manager.create_task(
        name=f"升级 {package_name}",
        package_name=package_name,
        task_type="upgrade",
    )

    async def run_upgrade():
        success, output = await task_manager.run_install_task(
            task_id=task.task_id,
            args=args,
            package_name=package_name,
        )
        return success, output

    background_tasks.add_task(run_upgrade)

    return TaskResponse(
        task_id=task.task_id,
        status="pending",
        message=f"任务已创建: 升级 {package_name}",
        output=None,
    )


@router.put("/{package_name}/version")
async def downgrade_package(package_name: str, version: str, background_tasks: BackgroundTasks):
    """降级包"""
    if not version:
        raise HTTPException(status_code=400, detail="version is required for downgrade")

    args = [sys.executable, "-m", "pip", "install", "--force-reinstall", f"{package_name}=={version}"]

    task = task_manager.create_task(
        name=f"降级 {package_name} 到 {version}",
        package_name=package_name,
        task_type="downgrade",
    )

    async def run_downgrade():
        success, output = await task_manager.run_install_task(
            task_id=task.task_id,
            args=args,
            package_name=package_name,
        )
        return success, output

    background_tasks.add_task(run_downgrade)

    return TaskResponse(
        task_id=task.task_id,
        status="pending",
        message=f"任务已创建: 降级 {package_name} 到 {version}",
        output=None,
    )
