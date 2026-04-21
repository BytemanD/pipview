"""Pydantic 数据校验模型"""

from typing import Optional

from pydantic import BaseModel


class PackageInfo(BaseModel):
    """包信息"""

    name: str
    version: str
    summary: Optional[str] = None
    home_page: Optional[str] = None
    author: Optional[str] = None
    author_email: Optional[str] = None
    license: Optional[str] = None
    requires_python: Optional[str] = None
    classifiers: Optional[list[str]] = None


class PackageListResponse(BaseModel):
    """包列表响应"""

    total: int
    packages: list[PackageInfo]


class PackageSearchResult(BaseModel):
    """包搜索结果"""

    name: str
    summary: str
    latest_version: str
    author: Optional[str] = None


class SourceInfo(BaseModel):
    """源信息"""

    name: str
    url: str
    priority: int = 0
    enabled: bool = True


class SourceListResponse(BaseModel):
    """源列表响应"""

    total: int
    sources: list[SourceInfo]


class InstallRequest(BaseModel):
    """安装请求"""

    package_name: str
    version: Optional[str] = None
    source: Optional[str] = None
    upgrade: bool = False
    extra_args: Optional[str] = None


class UninstallRequest(BaseModel):
    """卸载请求"""

    package_name: str
    force: bool = False


class UpgradeRequest(BaseModel):
    """升级请求"""

    package_name: Optional[str] = None
    version: Optional[str] = None
    all: bool = False


class TaskResponse(BaseModel):
    """任务响应"""

    task_id: str
    status: str
    message: str
    output: Optional[str] = None


class InstalledDistInfo(BaseModel):
    """pip show 返回的已安装包信息"""

    name: str
    version: str
    summary: Optional[str] = None
    home_page: Optional[str] = None
    author: Optional[str] = None
    author_email: Optional[str] = None
    license: Optional[str] = None
    requires: Optional[list[str]] = None
    required_by: Optional[list[str]] = None
    location: Optional[str] = None
    installer: Optional[str] = None
    metadata_version: Optional[str] = None
    classifiers: Optional[list[str]] = None
    requires_dist: Optional[list[str]] = None
    provides: Optional[list[str]] = None


class SourceConfig(BaseModel):
    """源配置"""

    name: str
    url: str
    timeout: int = 60
    trusted_host: bool = False


class TaskInfo(BaseModel):
    """任务信息"""

    task_id: str
    name: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    progress: int = 0
    message: str = ""
    output: Optional[str] = None
    package_name: Optional[str] = None
    task_type: str = "install"


class TaskListResponse(BaseModel):
    """任务列表响应"""

    total: int
    tasks: list[TaskInfo]
