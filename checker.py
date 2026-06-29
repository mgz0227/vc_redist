# checker.py
import winreg
from sysinfo import get_arch

def _reg_check(path):
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        v, _ = winreg.QueryValueEx(k, "Installed")
        return v == 1
    except:
        return False

def check_installed(version_key, arch):
    base = rf"SOFTWARE\Microsoft\VisualStudio\{version_key}\VC\Runtimes"
    if arch == "x64":
        return _reg_check(base + r"\x64")
    else:
        return _reg_check(base + r"\x86")

def get_missing(runtimes):
    return [r for r in runtimes if not check_installed(r["version_key"], r["arch"])]