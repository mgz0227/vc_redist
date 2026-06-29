# sysinfo.py
import platform
import struct

def get_arch():
    return "x64" if struct.calcsize("P") * 8 == 64 else "x86"

def get_os():
    return platform.system()

def is_windows():
    return platform.system().lower() == "windows"