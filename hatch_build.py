import shutil
import subprocess
import sys
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        frontend_dir = root / "frontend"
        static_dir = root / "src" / "pipview" / "static"

        if not frontend_dir.exists():
            print("Error: frontend directory not found")
            sys.exit(1)

        if not (frontend_dir / "package.json").exists():
            print("Error: package.json not found in frontend directory")
            sys.exit(1)

        if static_dir.exists():
            shutil.rmtree(static_dir)

        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=True)

        print("Building frontend...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True, shell=True)

        print(f"Frontend built to {static_dir}")