# checker.py
import winreg
from sysinfo import get_arch

REGISTRY_VIEWS = (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY, 0)

def _registry_views_for_arch(arch):
    if get_arch() != "x64":
        return (0,)
    if arch == "x64":
        return (winreg.KEY_WOW64_64KEY,)
    return (winreg.KEY_WOW64_32KEY,)

def _query_registry_value(path, arch, value_name):
    for view in _registry_views_for_arch(arch):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ | view) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
        except OSError:
            pass
    return None

def _reg_check(path, arch):
    try:
        for view in _registry_views_for_arch(arch):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ | view) as key:
                    for value_name in ("Installed", "Install"):
                        try:
                            value, _ = winreg.QueryValueEx(key, value_name)
                            if value == 1:
                                return True
                        except FileNotFoundError:
                            pass
            except OSError:
                pass
    except AttributeError:
        return False
    return False

def _default_registry_checks(version_key, arch):
    base = rf"SOFTWARE\Microsoft\VisualStudio\{version_key}\VC\Runtimes"
    return [base + rf"\{arch}"]

def check_installed(runtime):
    checks = runtime.get("registry_checks") or _default_registry_checks(runtime["version_key"], runtime["arch"])
    return any(_reg_check(path, runtime["arch"]) for path in checks)

def get_installed_version(runtime):
    checks = runtime.get("registry_checks") or _default_registry_checks(runtime["version_key"], runtime["arch"])
    for path in checks:
        value = _query_registry_value(path, runtime["arch"], "Version")
        if value:
            return str(value)
    return ""

def is_supported_arch(runtime):
    return get_arch() == "x64" or runtime["arch"] == "x86"

def get_missing(runtimes):
    return [r for r in runtimes if is_supported_arch(r) and not check_installed(r)]