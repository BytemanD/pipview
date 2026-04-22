"""任务管理模块"""

import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from pipview.common.logger import get_logger

logger = get_logger()


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务"""
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress: int = 0
    message: str = ""
    output: str = ""
    result: Optional[Any] = None
    error: Optional[str] = None
    package_name: Optional[str] = None
    task_type: str = "install"


class TaskManager:
    """任务管理器"""

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._lock = threading.Lock()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._subprocess_events: dict[str, asyncio.Event] = {}

    def create_task(self, name: str, package_name: str = "", task_type: str = "install") -> Task:
        """创建任务"""
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        task = Task(
            task_id=task_id,
            name=name,
            package_name=package_name,
            task_type=task_type,
        )
        with self._lock:
            self._tasks[task_id] = task
        logger.info(f"Task created: {task_id} - {name}")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> list[Task]:
        """获取所有任务"""
        with self._lock:
            tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)

    def get_active_tasks(self) -> list[Task]:
        """获取进行中的任务"""
        return self.get_all_tasks(status=TaskStatus.RUNNING)

    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务状态"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            return True

    def update_progress(self, task_id: str, progress: int, message: str = "") -> bool:
        """更新进度"""
        return self.update_task(task_id, progress=progress, message=message)

    def append_output(self, task_id: str, output: str) -> bool:
        """追加输出"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            task.output += output
            return True

    def complete_task(self, task_id: str, status: TaskStatus, result: Any = None, error: str = "") -> bool:
        """完成任务"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            task.status = status
            task.finished_at = datetime.now()
            task.result = result
            task.error = error
            logger.info(f"Task completed: {task_id} - status={status.value}")
            return True

    async def run_install_task(
        self,
        task_id: str,
        args: list[str],
        package_name: str,
        progress_callback: Optional[Callable] = None,
    ) -> tuple[bool, str]:
        """在后台运行安装任务"""
        import subprocess
        self.update_task(task_id, status=TaskStatus.RUNNING, started_at=datetime.now(), progress=0)
        self.append_output(task_id, f"Starting installation of {package_name}...\n")
        output_lines = []
        try:
            status, stdout = subprocess.getstatusoutput(args)
            if status == 0:
                self.complete_task(task_id, TaskStatus.SUCCESS, result={"package": package_name})
            else:
                logger.error(f"Task {task_id} failed: {stdout}")
                error_msg = "\n".join(output_lines[-10:]) if output_lines else "Installation failed"
                self.complete_task(task_id, TaskStatus.FAILED, error=error_msg)
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self.complete_task(task_id, TaskStatus.FAILED, error=str(e))
            return False, str(e)
        finally:
            self._subprocess_events.pop(task_id, None)
            self.update_progress(task_id, 100)

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        event = self._subprocess_events.get(task_id)
        if event:
            event.set()
        return self.update_task(task_id, status=TaskStatus.CANCELLED, finished_at=datetime.now())


task_manager = TaskManager()