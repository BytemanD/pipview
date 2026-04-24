"""pip 源管理服务"""

import configparser
import os
import urllib.parse
from pathlib import Path
from typing import Optional

from pipview.common.logger import get_logger

logger = get_logger()

DEFAULT_SOURCES = {
    "pypi": {
        "url": "https://pypi.org/simple",
        "priority": 1,
    },
    "aliyun": {
        "url": "https://mirrors.aliyun.com/pypi/simple",
        "priority": 2,
    },
    "tsinghua": {
        "url": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "priority": 3,
    },
    "douban": {
        "url": "https://pypi.doubanio.com/simple",
        "priority": 4,
    },
}


class SourceService:
    """源管理服务"""

    def __init__(self):
        self.pip_config_file = self._get_pip_config_file()

    def _get_pip_config_file(self) -> Path:
        """获取 pip 配置文件路径"""
        if os.name == "nt":
            pip_dir = Path(os.environ.get("APPDATA", "")) / "pip"
        else:
            pip_dir = Path.home() / ".config" / "pip"

        pip_dir.mkdir(parents=True, exist_ok=True)
        return pip_dir / "pip.ini"

    def get_pip_config(self) -> dict:
        """获取当前 pip 配置"""
        config = configparser.ConfigParser()

        if self.pip_config_file.exists():
            config.read(self.pip_config_file, encoding="utf-8")

        result = {}
        if config.has_section("global"):
            for key, value in config.items("global"):
                result[key] = value

        return result

    def get_sources(self) -> list[dict]:
        """获取实际配置的源"""
        config = self.get_pip_config()

        sources = []

        index_url = config.get("index-url", "https://pypi.org/simple")
        sources.append(
            {
                "name": "index-url",
                "url": index_url,
                "priority": 1,
                "enabled": True,
            }
        )

        if "extra-index-url" in config:
            extra_urls = config["extra-index-url"].split()
            for i, url in enumerate(extra_urls):
                sources.append(
                    {
                        "name": "extra-index-url",
                        "url": url,
                        "priority": i + 2,
                        "enabled": True,
                    }
                )

        return sources

    def _guess_source_name(self, url: str) -> str:
        """根据 URL 猜测源名称"""
        if "aliyun" in url:
            return "aliyun"
        elif "tsinghua" in url or "tuna" in url:
            return "tsinghua"
        elif "douban" in url:
            return "douban"
        elif "pypi" in url:
            return "pypi"
        return "custom"

    def set_source(self, source_url: str, extra_sources: Optional[list[str]] = None) -> bool:
        """设置 pip 源"""
        try:
            config = configparser.ConfigParser()

            if self.pip_config_file.exists():
                config.read(self.pip_config_file, encoding="utf-8")

            if not config.has_section("global"):
                config.add_section("global")

            config.set("global", "index-url", source_url)

            if source_url.startswith("http://"):
                parsed = urllib.parse.urlparse(source_url)
                config.set("global", "trusted-host", parsed.netloc)
            elif config.has_option("global", "trusted-host"):
                config.remove_option("global", "trusted-host")

            if extra_sources:
                config.set("global", "extra-index-url", "\n".join(extra_sources))
                for url in extra_sources:
                    if url.startswith("http://"):
                        parsed = urllib.parse.urlparse(url)
                        current_trusted = config.get("global", "trusted-host", "").split()
                        if parsed.netloc not in current_trusted:
                            current_trusted.append(parsed.netloc)
                        config.set("global", "trusted-host", " ".join(current_trusted))
            elif config.has_option("global", "extra-index-url"):
                config.remove_option("global", "extra-index-url")

            with open(self.pip_config_file, "w", encoding="utf-8") as f:
                config.write(f)

            logger.info("Set pip source to: {}", source_url)
            return True
        except Exception as e:
            logger.error("Failed to set pip source: {}", e)
            return False

    def add_source(self, name: str, url: str) -> bool:
        """添加额外源"""
        try:
            config = configparser.ConfigParser()

            if self.pip_config_file.exists():
                config.read(self.pip_config_file, encoding="utf-8")

            if not config.has_section("global"):
                config.add_section("global")

            extra_urls = []
            if config.has_option("global", "extra-index-url"):
                extra_urls = config.get("global", "extra-index-url").split()

            extra_urls.append(url)
            config.set("global", "extra-index-url", "\n".join(extra_urls))

            if url.startswith("http://"):
                parsed = urllib.parse.urlparse(url)
                current_trusted = config.get("global", "trusted-host", "").split()
                if parsed.netloc not in current_trusted:
                    current_trusted.append(parsed.netloc)
                config.set("global", "trusted-host", " ".join(current_trusted))

            with open(self.pip_config_file, "w", encoding="utf-8") as f:
                config.write(f)

            logger.info("Added pip source: {} -> {}", name, url)
            return True
        except Exception as e:
            logger.error("Failed to add pip source: {}", e)
            return False

    def remove_source(self, name: str) -> bool:
        """移除额外源"""
        try:
            config = configparser.ConfigParser()

            if self.pip_config_file.exists():
                config.read(self.pip_config_file, encoding="utf-8")

            if not config.has_section("global"):
                return True

            if config.has_option("global", name):
                config.get("global", name).split()
                config.remove_option("global", name)
                with open(self.pip_config_file, "w", encoding="utf-8") as f:
                    config.write(f)

            logger.info("Removed pip source: {}", name)
            return True
        except Exception as e:
            logger.error("Failed to remove pip source: {}", e)
            return False

    def reset_to_default(self) -> bool:
        """重置为默认源"""
        try:
            if self.pip_config_file.exists():
                os.remove(self.pip_config_file)
            logger.info("Reset pip source to default")
            return True
        except Exception as e:
            logger.error("Failed to reset pip source: {}", e)
            return False


source_service = SourceService()
