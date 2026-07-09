# sysinfo.py
import platform

def get_arch():
    machine = platform.machine().lower()
    return "x64" if machine in ("amd64", "x86_64", "arm64", "aarch64") else "x86"

def get_os():
    return platform.system()

def is_windows():
    return platform.system().lower() == "windows"