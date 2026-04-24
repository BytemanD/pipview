"""配置 API 端点"""

import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter

from pipview.common.config import CONF

router = APIRouter(prefix="/configs", tags=["configs"])


def read_pip_config() -> Optional[str]:
    """读取 pip 配置文件原始内容"""
    if os.name == "nt":
        pip_dir = Path(os.environ.get("APPDATA", "")) / "pip"
    else:
        pip_dir = Path.home() / ".config" / "pip"

    pip_config_file = pip_dir / "pip.ini"

    if pip_config_file.exists():
        return pip_config_file.read_text(encoding="utf-8")
    return None


@router.get("")
async def get_config():
    """获取当前配置"""
    return {
        "app": {
            "name": CONF.app.name,
            "version": CONF.app.version,
            "debug": CONF.app.debug,
            "host": CONF.app.host,
            "port": CONF.app.port,
        },
        "log": {
            "level": CONF.log.log_level,
            "dir": CONF.log.log_dir,
            "retention_days": CONF.log.log_retention_days,
        },
    }


@router.get("/pip")
async def get_pip_config():
    """获取 pip 配置原始内容"""
    content = read_pip_config()

    return {
        "exists": content is not None,
        "content": content,
    }


@router.get("/env")
async def get_env():
    """获取环境变量"""
    lines = []
    for key in ["PIP_INDEX_URL", "PIP_TRUSTED_HOST", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"]:
        if key in os.environ:
            lines.append(f"{key}={os.environ[key]}")

    return {"content": "\n".join(lines) if lines else ""}


@router.get("/python-version")
async def get_python_version():
    """获取 Python 版本"""
    return {"version": sys.version}


@router.get("/pip-version")
async def get_pip_version():
    """获取 pip 版本"""
    try:
        import pip

        return {"version": pip.__version__, "installed": True}
    except ImportError:
        return {"version": None, "installed": False}


@router.post("/install-pip")
async def install_pip():
    """安装 pip (使用 ensurepip)"""
    import subprocess

    try:
        p = subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            capture_output=True,
            text=True,
        )
        if p.returncode == 0:
            import pip

            return {"success": True, "version": pip.__version__}
        return {"success": False, "output": p.stdout + p.stderr}
    except Exception as e:
        return {"success": False, "output": str(e)}
