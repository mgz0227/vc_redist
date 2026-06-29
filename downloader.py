# downloader.py
import os, requests, hashlib
from concurrent.futures import ThreadPoolExecutor

def sha256_file(p):
    h = hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

def download_one(item, out, cb=None):
    url = item["url"]
    path = os.path.join(out, url.split("/")[-1])
    r = requests.get(url, stream=True, timeout=30)

    total = int(r.headers.get("content-length",0))
    cur = 0

    with open(path,"wb") as f:
        for chunk in r.iter_content(1024*256):
            if chunk:
                f.write(chunk)
                cur += len(chunk)
                if cb:
                    cb(item["name"],cur,total)

    return path

def download_all(items, out="downloads", cb=None):
    os.makedirs(out, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        return list(ex.map(lambda i: download_one(i,out,cb), items))