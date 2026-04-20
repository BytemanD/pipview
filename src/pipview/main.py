"""应用主入口"""

from pipview.common.config import CONF

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pipview.server:app",
        host=CONF.app.host,
        port=CONF.app.port,
        reload=True,
    )
