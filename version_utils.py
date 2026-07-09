# version_utils.py
import re
import subprocess
import tempfile
from pathlib import Path

import requests

from downloader import download_file
from paths import resolve_project_path


REQUEST_TIMEOUT = (10, 30)

def parse_version(value):
    if not value:
        return ()
    match = re.search(r"\d+(?:\.\d+){1,3}", str(value))
    version_text = match.group(0) if match else str(value).strip()
    parts = []
    for part in version_text.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            digits = "".join(ch for ch in part if ch.isdigit())
            parts.append(int(digits) if digits else 0)
    return tuple(parts)


def compare_versions(left, right):
    left_parts = parse_version(left)
    right_parts = parse_version(right)
    size = max(len(left_parts), len(right_parts))
    left_parts += (0,) * (size - len(left_parts))
    right_parts += (0,) * (size - len(right_parts))
    return (left_parts > right_parts) - (left_parts < right_parts)


def get_file_version(path):
    package = resolve_project_path(path)
    if not package.is_file():
        return ""
    command = "$v=(Get-Item -LiteralPath $args[0]).VersionInfo; if ($v.ProductVersion) { $v.ProductVersion } else { $v.FileVersion }"
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command, str(package)],
        capture_output=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def get_cloud_package_info(runtime):
    with requests.head(
        runtime["url"],
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
        headers={"User-Agent": "VC-Redist-Manager/1.0"},
    ) as response:
        response.raise_for_status()
        return {
            "url": response.url,
            "size": int(response.headers.get("content-length", 0) or 0),
            "last_modified": response.headers.get("last-modified", ""),
        }


def download_latest_package(runtime, cb=None):
    folder = Path(tempfile.gettempdir()) / "vc_redist_latest"
    path = folder / f'{runtime["id"]}.exe'
    latest_path = download_file(
        runtime["url"], path, name=runtime["name"], cb=cb, reuse_existing=False
    )
    return latest_path, get_file_version(latest_path)
