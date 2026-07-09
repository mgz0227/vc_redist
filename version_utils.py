# version_utils.py
import os
import re
import subprocess
import tempfile

import requests


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
    command = "$v=(Get-Item -LiteralPath $args[0]).VersionInfo; if ($v.ProductVersion) { $v.ProductVersion } else { $v.FileVersion }"
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command, path],
        capture_output=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def get_cloud_package_info(runtime):
    response = requests.head(runtime["url"], timeout=15, allow_redirects=True)
    response.raise_for_status()
    return {
        "url": response.url,
        "size": int(response.headers.get("content-length", 0) or 0),
        "last_modified": response.headers.get("last-modified", ""),
    }


def download_latest_package(runtime, cb=None):
    folder = os.path.join(tempfile.gettempdir(), "vc_redist_latest")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{runtime["id"]}.exe')

    response = requests.get(runtime["url"], stream=True, timeout=30, allow_redirects=True)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    current = 0
    with open(path, "wb") as file:
        for chunk in response.iter_content(1024 * 256):
            if chunk:
                file.write(chunk)
                current += len(chunk)
                if cb:
                    cb(runtime["name"], current, total)

    return path, get_file_version(path)