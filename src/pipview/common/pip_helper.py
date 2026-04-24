"""pip 辅助模块 - 处理虚拟环境中没有 pip 的情况"""

import subprocess
import sys
from typing import Optional

from pipview.common.logger import get_logger

logger = get_logger()


def has_pip() -> bool:
    """检查当前环境是否有 pip"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            timeout=5,
        )
        return True
    except Exception:
        return False


def install_pip() -> bool:
    """使用 ensurepip 安装 pip"""
    if has_pip():
        return True

    logger.info(" pip not found, attempting to install via ensurepip...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            logger.info(" pip installed successfully")
            return True
        else:
            logger.error("Failed to install pip: {}", result.stderr)
            return False
    except Exception as e:
        logger.error("Error installing pip: {}", e)
        return False


def ensure_pip() -> bool:
    """确保 pip 可用"""
    if has_pip():
        return True
    return install_pip()


def get_pip_command(
    *args: str,
    extra_args: Optional[str] = None,
) -> list[str]:
    """获取 pip 命令列表"""
    cmd = [sys.executable, "-m", "pip"]

    if extra_args:
        cmd.extend(extra_args.split())

    cmd.extend(args)
    return cmd
