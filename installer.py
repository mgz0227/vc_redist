# installer.py
import os
import shlex
import subprocess

def install(exe, args):
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.run([exe, *shlex.split(args)], creationflags=creationflags).returncode

def install_all(files, runtimes=None, cb=None):
    res = {}
    if runtimes is None:
        runtimes = []

    by_path = {os.path.normcase(os.path.abspath(f)): f for f in files}
    for item in runtimes:
        offline_path = item.get("_install_path") or item.get("offline_path")
        exe = by_path.get(os.path.normcase(os.path.abspath(offline_path))) if offline_path else None
        if exe:
            if cb:
                cb(item["name"], "start", None)
            code = install(exe, item["silent_args"])
            res[item["name"]] = code
            if cb:
                cb(item["name"], "done", code)
    return res