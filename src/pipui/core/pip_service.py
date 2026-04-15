"""包服务模块"""

import subprocess
import sys
from importlib.metadata import PackageNotFoundError, distribution, distributions
from typing import Optional

from pipui.common.http import http_get
from pipui.common.logger import get_logger

logger = get_logger()

logger = get_logger()


class PackageService:
    """包服务"""

    def list_packages(self, search: Optional[str] = None) -> dict:
        """列出已安装的包"""
        all_packages = []
        seen_names = set()
        for dist in distributions():
            name = dist.metadata.get("Name") or dist.metadata.get("Project-Name")
            if name and name not in seen_names:
                seen_names.add(name)
                try:
                    pkg_info = {
                        "name": name,
                        "version": dist.version,
                        "author": dist.metadata.get("Author", ""),
                    }
                    all_packages.append(pkg_info)
                except Exception as e:
                    logger.warning(f"Failed to get info for {name}: {e}")

        if search:
            search_lower = search.lower()
            all_packages = [p for p in all_packages if search_lower in p.get("name", "").lower()]

        return {
            "total": len(all_packages),
            "packages": all_packages,
        }

    def get_package_info(self, package_name: str) -> dict:
        """获取包详细信息"""
        try:
            dist = distribution(package_name)
            meta = dist.metadata
            return {
                "name": meta.get("Name") or package_name,
                "version": dist.version,
                "summary": meta.get("Summary", ""),
                "home-page": meta.get("Home-page", ""),
                "author": meta.get("Author", ""),
                "author-email": meta.get("Author-email", ""),
                "license": meta.get("License", ""),
                "requires-python": meta.get("Requires-Python", ""),
                "classifiers": meta.get_all("Classifier") or [],
                "keywords": meta.get("Keywords", ""),
                "description": meta.get("Description", ""),
            }
        except PackageNotFoundError:
            return {}

    def search_packages(self, query: str, timeout: int = 30) -> list[dict]:
        """搜索包 (使用 PyPI API)"""
        import httpx

        try:
            resp = httpx.get(
                f"https://pypi.org/pypi/{query}/json",
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                info = data.get("info", {})
                return [
                    {
                        "name": info.get("name"),
                        "version": info.get("version"),
                        "summary": info.get("summary"),
                    }
                ]
        except Exception as e:
            logger.error(f"Failed to search packages: {e}")
        return []

    async def install_package(
        self,
        package_name: str,
        version: Optional[str] = None,
        upgrade: bool = False,
        extra_args: Optional[str] = None,
    ) -> tuple[bool, str]:
        """安装包"""
        args = [sys.executable, "-m", "pip", "install"]

        if upgrade:
            args.append("--upgrade")
        else:
            args.append("-y")

        if version:
            args.append(f"{package_name}=={version}")
        else:
            args.append(package_name)

        if extra_args:
            args.extend(extra_args.split())

        logger.info(f"Running: {' '.join(args)}")

        try:
            p = subprocess.run(
                args,
                capture_output=True,
                text=True,
            )
            success = p.returncode == 0
            output = p.stdout + p.stderr if not success else p.stdout
            return success, output
        except Exception as e:
            logger.error(f"Failed to install package: {e}")
            return False, str(e)

    async def uninstall_package(self, package_name: str, force: bool = True) -> tuple[bool, str]:
        """卸载包"""
        args = [sys.executable, "-m", "pip", "uninstall", "-y"]
        args.append(package_name)

        logger.info(f"Running: {' '.join(args)}")

        try:
            p = subprocess.run(
                args,
                capture_output=True,
                text=True,
            )
            success = p.returncode == 0
            output = p.stdout + p.stderr if not success else p.stdout
            return success, output
        except Exception as e:
            logger.error(f"Failed to uninstall package: {e}")
            return False, str(e)

    async def upgrade_package(self, package_name: str) -> tuple[bool, str]:
        """升级包"""
        return await self.install_package(package_name, upgrade=True)

    async def upgrade_all(self) -> tuple[bool, str]:
        """升级所有包"""
        args = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]

        try:
            p = subprocess.run(args, capture_output=True, text=True)
            if p.returncode != 0:
                return True, "没有需要升级的包"

            import json

            try:
                outdated = json.loads(p.stdout)
            except json.JSONDecodeError:
                return True, "没有需要升级的包"

            if not outdated:
                return True, "没有需要升级的包"

            package_names = [pkg["name"] for pkg in outdated]
            upgrade_args = [sys.executable, "-m", "pip", "install", "--upgrade"] + package_names

            logger.info(f"Running: {' '.join(upgrade_args)}")

            p = subprocess.run(upgrade_args, capture_output=True, text=True)
            success = p.returncode == 0
            output = p.stdout + p.stderr if not success else p.stdout
            return success, output
        except Exception as e:
            logger.error(f"Failed to upgrade packages: {e}")
            return False, str(e)

    async def downgrade_package(self, package_name: str, version: str) -> tuple[bool, str]:
        """降级包到指定版本"""
        args = [sys.executable, "-m", "pip", "install", "--force-reinstall", f"{package_name}=={version}"]

        logger.info(f"Running: {' '.join(args)}")

        try:
            p = subprocess.run(args, capture_output=True, text=True)
            success = p.returncode == 0
            output = p.stdout + p.stderr if not success else p.stdout
            return success, output
        except Exception as e:
            logger.error(f"Failed to downgrade package: {e}")
            return False, str(e)

    async def check_conflicts(self) -> dict:
        """检查包冲突"""
        args = [sys.executable, "-m", "pip", "check"]

        try:
            p = subprocess.run(args, capture_output=True, text=True)
            if p.returncode == 0:
                return {"ok": True, "output": "No broken requirements"}

            return {"ok": False, "output": p.stdout.strip() + p.stderr.strip()}
        except Exception as e:
            logger.error(f"Failed to check conflicts: {e}")
            return {"ok": True, "output": "", "error": str(e)}

    async def get_package_versions(self, package_name: str) -> list[str]:
        """获取包所有可用版本"""
        try:
            data = await http_get(f"https://pypi.org/pypi/{package_name}/json")
            releases = data.get("releases", {})
            versions = list(releases.keys())
            versions.sort(
                key=lambda x: tuple(map(int, x.split("."))) if x.replace(".", "").isdigit() else (0,), reverse=True
            )
            return versions
        except Exception as e:
            logger.error(f"Failed to get versions: {e}")
            return []


package_service = PackageService()
