# installer.py
import os
import subprocess

def install(exe, args):
    return subprocess.run(f'"{exe}" {args}', shell=True).returncode

def install_all(files, runtimes=None):
    res = {}
    if runtimes is None:
        runtimes = []

    by_path = {os.path.normcase(os.path.abspath(f)): f for f in files}
    for item in runtimes:
        offline_path = item.get("offline_path")
        exe = by_path.get(os.path.normcase(os.path.abspath(offline_path))) if offline_path else None
        if exe:
            res[item["name"]] = install(exe, item["silent_args"])
    return res