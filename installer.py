# installer.py
import subprocess, os

def install(exe, args):
    return subprocess.run(f'"{exe}" {args}', shell=True).returncode

def install_all(files, runtimes):
    res = {}
    for f in files:
        name = os.path.basename(f)
        m = next((r for r in runtimes if r["url"].split("/")[-1]==name),None)
        if m:
            res[name] = install(f, m["silent_args"])
    return res