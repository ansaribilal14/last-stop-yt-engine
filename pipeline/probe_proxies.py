#!/usr/bin/env python3
"""probe_proxies.py — find working egress proxies for yt-dlp (R8: local-only).
Fetches free-proxy lists, validates each with a REAL yt-dlp metadata call
(playability check), writes /tmp/good_proxies.json.
Usage: probe_proxies.py [max_good=10] [timeout_s=25]
"""
import concurrent.futures as cf
import json, os, random, subprocess, sys, urllib.request

OUT = "/tmp/good_proxies.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

def fetch_list(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        txt = urllib.request.urlopen(req, timeout=15).read().decode()
        out = []
        for line in txt.strip().splitlines():
            line = line.strip()
            if ":" in line and line.replace(":", "").replace(".", "").isdigit():
                ip, port = line.split(":")[:2]
                out.append(f"http://{ip}:{port}")
        return out
    except Exception:
        return []

def works(proxy):
    try:
        r = subprocess.run(
            ["yt-dlp","--no-cache-dir","--no-check-certificates","--proxy",proxy,
             "--extractor-args","youtube:player_client=tv_simply",
             "--extractor-args","youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416",
             "--simulate","--print","%(id)s",
             "https://www.youtube.com/watch?v=IHNzOHi8sJs"],
            capture_output=True, text=True, timeout=int(os.environ.get("PTO","25")))
        return proxy if r.returncode == 0 and "IHNzOHi8sJs" in r.stdout else None
    except Exception:
        return None

def main():
    max_good = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    lists = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    ]
    pool = []
    for u in lists:
        got = fetch_list(u)
        print(f"{u.split('/')[5] if len(u.split('/'))>5 else u}: {len(got)}", flush=True)
        pool += got
    random.shuffle(pool)
    pool = pool[:220]
    good = []
    with cf.ThreadPoolExecutor(max_workers=24) as ex:
        for res in ex.map(works, pool):
            if res:
                good.append({"url": res})
                print(f"  GOOD {res}", flush=True)
                if len(good) >= max_good: break
    json.dump(good, open(OUT, "w"))
    print(f"WROTE {len(good)} -> {OUT}", flush=True)

if __name__ == "__main__":
    main()
