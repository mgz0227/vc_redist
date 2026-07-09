# installer.py
"""Silent installer execution and result classification."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Callable

from downloader import package_validation_error
from paths import resolve_project_path


SUCCESS_CODES = {0, 1638, 3010, 1641}
RESTART_CODES = {3010, 1641}
InstallCallback = Callable[[str, str, int | str | None], None]


def install_result_text(code: int | None) -> str:
    messages = {
        0: "安装完成",
        1638: "已安装相同或更高版本",
        3010: "安装完成，需要重启 Windows",
        1641: "安装完成，安装程序请求重启 Windows",
        None: "安装程序未能启动",
    }
    return messages.get(code, f"安装程序返回代码 {code}")


def install(exe: str | Path, args: str, expected_sha256: str = "") -> int:
    package = resolve_project_path(exe)
    validation_error = package_validation_error(package, expected_sha256)
    if validation_error:
        raise ValueError(f"无法安装 {package.name}：{validation_error}")

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    command = [str(package), *shlex.split(args, posix=False)]
    return subprocess.run(command, creationflags=creationflags, check=False).returncode


def _normalised_path(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(resolve_project_path(path)))


def install_all(
    files: list[str], runtimes: list[dict] | None = None, cb: InstallCallback | None = None
) -> dict[str, int | None]:
    """Install the supplied runtime files, continuing after an individual error."""
    results: dict[str, int | None] = {}
    runtimes = runtimes or []
    by_path = {_normalised_path(file): file for file in files}

    for item in runtimes:
        configured_path = item.get("_install_path") or item.get("offline_path")
        executable = by_path.get(_normalised_path(configured_path)) if configured_path else None
        if not executable:
            continue

        if cb:
            cb(item["name"], "start", None)
        try:
            expected_sha256 = item.get(
                "_install_sha256", item.get("offline_sha256", item.get("sha256", ""))
            )
            code = install(executable, item["silent_args"], expected_sha256)
        except (OSError, ValueError) as exc:
            results[item["name"]] = None
            if cb:
                cb(item["name"], "error", str(exc))
            continue

        results[item["name"]] = code
        if cb:
            cb(item["name"], "done", code)
    return results
