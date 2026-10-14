#!/usr/bin/env python3
"""vk_scan.py — scrape a vkvideo channel/search page and print video URLs+titles.
Usage: python3 scripts/vk_scan.py <url> [max_links]"""
import re, sys, json, urllib.request

def fetch(url):
    from curl_cffi import requests as creq
    r = creq.get(url, impersonate="firefox", timeout=30,
                 headers={"Accept-Language": "en-US,en;q=0.9,ko;q=0.8"})
    return r.text

def main():
    url, maxn = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
    h = fetch(url)
    vids = {}
    for m in re.finditer(r'video(-?\d+_\d+)["\'?]?', h):
        vids.setdefault(m.group(1), None)
    # try to pair with nearby titles
    out = []
    seen = set()
    for vid in vids:
        if vid in seen: continue
        seen.add(vid)
        # find title near the id occurrence
        idx = h.find(vid)
        seg = h[max(0, idx - 600): idx + 200]
        t = re.search(r'(?:title|aria-label)="([^"]{8,110})"', seg)
        out.append((f"https://vkvideo.ru/video{vid}", t.group(1) if t else "?"))
        if len(out) >= maxn: break
    for u, t in out:
        print(f"{u} | {t}")

if __name__ == "__main__":
    main()
