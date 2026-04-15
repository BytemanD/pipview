"""项目配置模块"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    name: str = "pipui"
    version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


class LogSettings(BaseSettings):
    """日志配置"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    log_level: str = "INFO"
    log_dir: str = "logs"
    log_retention_days: int = 7


class Settings(BaseSettings):
    """全局配置集合"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app: AppSettings = Field(default_factory=AppSettings)
    log: LogSettings = Field(default_factory=LogSettings)


CONF = Settings()
