#!/usr/bin/env python3
"""probe_proxies2.py — two-stage proxy hunt.
scan: TCP-connect prefilter over all list proxies -> /tmp/proxy_alive.json
test: yt-dlp metadata validation (tv_simply) on survivors -> /tmp/good_proxies.json
Usage: probe_proxies2.py scan | test | all      (PTO env = per-attempt timeout)
"""
import concurrent.futures as cf
import json, os, random, socket, subprocess, sys, urllib.request

OUT = "/tmp/good_proxies.json"
ALIVE = "/tmp/proxy_alive.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

def fetch_list(url, scheme):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        txt = urllib.request.urlopen(req, timeout=20).read().decode()
        out = []
        for line in txt.strip().splitlines():
            line = line.strip()
            if ":" in line and line.replace(":", "").replace(".", "").isdigit():
                ip, port = line.split(":")[:2]
                out.append((scheme, ip, int(port)))
        return out
    except Exception:
        return []

def tcp_ok(item):
    sch, ip, port = item
    try:
        s = socket.create_connection((ip, port), timeout=2.5)
        s.close()
        return item
    except Exception:
        return None

def ytdlp_ok(proxy, client="tv_simply"):
    try:
        r = subprocess.run(
            ["python3", "-m", "yt_dlp", "--no-cache-dir", "--no-check-certificates",
             "--js-runtimes", "node", "--proxy", proxy,
             "--extractor-args", f"youtube:player_client={client}",
             "--extractor-args", "youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416",
             "--simulate", "--print", "%(id)s",
             "https://www.youtube.com/watch?v=IHNzOHi8sJs"],
            capture_output=True, text=True,
            timeout=int(os.environ.get("PTO", "15")))
        return proxy if r.returncode == 0 and "IHNzOHi8sJs" in r.stdout else None
    except Exception:
        return None

def scan():
    lists = [
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt", "socks5"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt", "socks5"),
        ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "http"),
        ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", "http"),
        ("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt", "socks5"),
    ]
    pool = []
    for u, sch in lists:
        got = fetch_list(u, sch)
        print(f"{sch} {u.split('/')[4]}: {len(got)}", flush=True)
        pool += got
    pool = list({(s, i, p) for s, i, p in pool})
    random.shuffle(pool)
    print(f"total unique: {len(pool)}", flush=True)
    alive = []
    with cf.ThreadPoolExecutor(max_workers=64) as ex:
        for res in ex.map(tcp_ok, pool):
            if res:
                alive.append(res)
    alive.sort(key=lambda x: 0 if x[0] == "socks5" else 1)
    json.dump(alive, open(ALIVE, "w"))
    print(f"tcp-alive {len(alive)} -> {ALIVE}", flush=True)

def test(batch=260, want=6):
    if not os.path.exists(ALIVE):
        sys.exit("run scan first")
    alive = [tuple(x) for x in json.load(open(ALIVE))]
    cands = [f"{sch}://{ip}:{port}" for sch, ip, port in alive][:batch]
    print(f"validating {len(cands)} (tv_simply)", flush=True)
    good = []
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(ytdlp_ok, p, "tv_simply"): p for p in cands}
        for f in cf.as_completed(futs):
            res = f.result()
            if res:
                print(f"  GOOD {res}", flush=True)
                good.append({"url": res})
                if len(good) >= want:
                    break
    json.dump(good, open(OUT, "w"))
    print(f"WROTE {len(good)} -> {OUT}", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "scan":
        scan()
    elif mode == "test":
        test()
    else:
        scan(); test()
