"""任务管理 API 端点"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from pipview.core.task_manager import TaskStatus, task_manager
from pipview.core.schemas import TaskInfo, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_to_info(task) -> TaskInfo:
    """转换任务为 TaskInfo"""
    return TaskInfo(
        task_id=task.task_id,
        name=task.name,
        status=task.status.value,
        created_at=task.created_at.isoformat() if task.created_at else "",
        started_at=task.started_at.isoformat() if task.started_at else None,
        finished_at=task.finished_at.isoformat() if task.finished_at else None,
        progress=task.progress,
        message=task.message,
        output=task.output or None,
        package_name=task.package_name,
        task_type=task.task_type,
    )


@router.get("")
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
):
    """获取任务列表"""
    task_status = TaskStatus(status) if status else None
    tasks = task_manager.get_all_tasks(status=task_status)[:limit]
    return TaskListResponse(
        total=len(tasks),
        tasks=[_task_to_info(t) for t in tasks],
    )


@router.get("/active")
async def list_active_tasks():
    """获取进行中的任务"""
    tasks = task_manager.get_active_tasks()
    return TaskListResponse(
        total=len(tasks),
        tasks=[_task_to_info(t) for t in tasks],
    )


@router.get("/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return _task_to_info(task)


@router.get("/{task_id}/output")
async def get_task_output(task_id: str):
    """获取任务输出"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return {"task_id": task_id, "output": task.output or "", "status": task.status.value}


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """取消任务"""
    success = task_manager.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return {"task_id": task_id, "status": "cancelled"}