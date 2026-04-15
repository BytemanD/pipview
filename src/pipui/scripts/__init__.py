"""构建脚本"""

import shutil
import subprocess
import sys
from pathlib import Path


def build_frontend():
    """构建前端 Vue 应用"""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    dist_dir = frontend_dir / "dist"

    if not frontend_dir.exists():
        print("Error: frontend directory not found")
        sys.exit(1)

    if not (frontend_dir / "package.json").exists():
        print("Error: package.json not found in frontend directory")
        sys.exit(1)

    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    print("Installing dependencies...")
    subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)

    print("Building frontend...")
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)

    print(f"Build complete! Output in {dist_dir}")


if __name__ == "__main__":
    build_frontend()
