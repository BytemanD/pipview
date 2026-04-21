"""应用主入口"""

from pipview import server

if __name__ == "__main__":
    server.run(
        _app="pipview.server:app",
        reload=True,
    )

