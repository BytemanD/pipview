# PipView

一个现代化的 Python pip 包管理 Web 面板。

## 功能特性

- 📦 **包管理**: 查看、安装、卸载已安装的 Python 包
- 🔄 **批量升级**: 一键升级所有可升级的包
- 🌍 **源管理**: 快速切换 pip 镜像源
- 🎨 **现代化 UI**: 简洁美观的 Web 界面

## 技术栈

- **后端**: FastAPI + SQLAlchemy (异步)
- **前端**: 原生 HTML + CSS + JavaScript
- **配置**: Pydantic Settings
- **日志**: Loguru
- **包管理**: uv

## 快速开始

### 安装依赖

```bash
cd pipview
uv sync
```

### 启动服务

```bash
uv run python -m pipview.main
```

服务启动后，访问 http://localhost:8000

### 开发模式

```bash
# 启用调试模式
export APP_DEBUG=true
uv run python -m pipview.main
```

## 配置说明

在 `.env` 文件中配置以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `APP_DEBUG` | false | 是否启用调试模式 |
| `APP_HOST` | 0.0.0.0 | 服务监听地址 |
| `APP_PORT` | 8000 | 服务监听端口 |
| `LOG_LEVEL` | INFO | 日志级别 |
| `LOG_DIR` | logs | 日志目录 |

## API 文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
pipview/
├── src/pipview/
│   ├── api/v1/          # API 路由
│   │   └── endpoints/  # API 端点
│   ├── common/         # 公共模块
│   ├── core/          # 核心业务逻辑
│   └── static/        # 静态文件
├── .env.example       # 环境变量模板
└── pyproject.toml    # 项目配置
```

## License

MIT