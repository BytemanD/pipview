"""日志配置模块"""

import sys
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from pipui.common.config import CONF

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


class LogFormatter:
    """自定义日志格式，集成 trace_id"""

    def format(self, record: dict[str, Any]) -> str:
        trace_id = trace_id_var.get()
        if trace_id:
            record["extra"]["trace_id"] = trace_id

        return "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"


def setup_log() -> None:
    """初始化日志系统"""
    log_dir = Path(CONF.log.log_dir)
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    log_format = LogFormatter()

    logger.add(
        sys.stdout,
        format=log_format.format,
        level=CONF.log.log_level,
        colorize=True,
    )

    log_file_path = log_dir / f"pipui-{datetime.now().strftime('%Y-%m-%d')}.log"
    logger.add(
        log_file_path,
        format=log_format.format,
        level=CONF.log.log_level,
        rotation="1 day",
        retention=f"{CONF.log.log_retention_days} days",
        compression="zip",
        encoding="utf-8",
    )


def get_logger():
    """获取日志实例"""
    return logger
