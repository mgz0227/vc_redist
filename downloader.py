# downloader.py
"""Download and validate Visual C++ installer packages."""

from __future__ import annotations

import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

import requests

from paths import resolve_project_path


CHUNK_SIZE = 256 * 1024
MIN_EXECUTABLE_SIZE = 1024
REQUEST_TIMEOUT = (10, 60)
ProgressCallback = Callable[[str, int, int], None]


class DownloadError(RuntimeError):
    """Raised when a package cannot be retrieved or verified."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_validation_error(path: str | Path, expected_sha256: str = "") -> str | None:
    """Return a human-readable validation problem, or ``None`` for a usable EXE."""
    package = Path(path)
    if not package.is_file():
        return "安装包不存在"
    if package.stat().st_size < MIN_EXECUTABLE_SIZE:
        return "安装包大小异常"

    try:
        with package.open("rb") as file:
            if file.read(2) != b"MZ":
                return "安装包不是有效的 Windows 可执行文件"
    except OSError as exc:
        return f"无法读取安装包：{exc}"

    expected = expected_sha256.strip().lower()
    if expected and sha256_file(package).lower() != expected:
        return "安装包校验和不匹配"
    return None


def _download_target(item: dict, out: str | Path) -> Path:
    offline_path = item.get("offline_path")
    if offline_path:
        return resolve_project_path(offline_path)
    filename = item["url"].rstrip("/").split("/")[-1] or f'{item["id"]}.exe'
    return resolve_project_path(Path(out) / f'{item["id"]}_{filename}')


def download_file(
    url: str,
    destination: str | Path,
    *,
    name: str,
    expected_sha256: str = "",
    cb: ProgressCallback | None = None,
    reuse_existing: bool = True,
) -> str:
    """Download a file atomically so interrupted transfers never look complete."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)

    existing_error = package_validation_error(target, expected_sha256)
    if reuse_existing and existing_error is None:
        size = target.stat().st_size
        if cb:
            cb(name, size, size)
        return str(target)

    partial = target.with_name(f"{target.name}.part")
    current = 0

    try:
        with requests.get(
            url,
            stream=True,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": "VC-Redist-Manager/1.0"},
        ) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0) or 0)
            with partial.open("wb") as file:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)
                        current += len(chunk)
                        if cb:
                            cb(name, current, total)
    except requests.RequestException as exc:
        raise DownloadError(f"下载 {name} 失败：{exc}") from exc
    except OSError as exc:
        raise DownloadError(f"保存 {name} 失败：{exc}") from exc

    validation_error = package_validation_error(partial, expected_sha256)
    if validation_error:
        raise DownloadError(f"{name} 下载完成后校验失败：{validation_error}")

    os.replace(partial, target)
    return str(target)


def download_one(item: dict, out: str | Path, cb: ProgressCallback | None = None) -> str:
    return download_file(
        item["url"],
        _download_target(item, out),
        name=item["name"],
        expected_sha256=item.get("sha256", ""),
        cb=cb,
    )


def download_all(
    items: list[dict], out: str | Path = "downloads", cb: ProgressCallback | None = None
) -> list[str]:
    """Download independent packages concurrently while preserving item order."""
    if not items:
        return []

    output = resolve_project_path(out)
    output.mkdir(parents=True, exist_ok=True)
    workers = min(4, len(items))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(lambda item: download_one(item, output, cb), items))
