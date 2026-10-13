#!/usr/bin/env python3
"""upload_storageto.py — storage.to REST API uploader (3-step presigned flow).
Usage: upload_storageto.py <file> [content_type]
Implements: /upload/init -> parallel PUT parts -> /upload/parts -> /complete-multipart -> /confirm
Docs: per spec paste (33 endpoints, anonymous 25GB max, multipart >50MB).
"""
import concurrent.futures as cf
import hashlib, json, os, sys, time, urllib.request

BASE = "https://storage.to/api"
VISITOR = "lsengine-" + hashlib.sha256(os.uname().nodename.encode()).hexdigest()[:16]

def api(path, payload=None, extra=None):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Content-Type": "application/json", "X-Visitor-Token": VISITOR, **(extra or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def put_part(url, path):
    for attempt in range(3):
        try:
            with open(path, "rb") as f:
                req = urllib.request.Request(url, data=f.read(), method="PUT")
                with urllib.request.urlopen(req, timeout=600) as r:
                    return r.headers.get("ETag")
        except Exception as e:
            print(f"    part retry {attempt+1}: {e}", flush=True); time.sleep(2)
    return None

def main():
    fp = sys.argv[1]; ct = sys.argv[2] if len(sys.argv) > 2 else "video/mp4"
    size = os.path.getsize(fp)
    print(f"init {fp} ({size} bytes) visitor={VISITOR}", flush=True)
    init = api("/upload/init", {"filename": os.path.basename(fp), "content_type": ct, "size": size})
    if not init.get("success"):
        print("INIT FAILED:", init); sys.exit(1)
    print("type:", init.get("type"), flush=True)
    if init.get("type") == "single":
        etag = put_part(init["upload_url"], fp)
        assert etag, "single PUT failed"
        r2key = init["r2_key"]
    else:
        upload_id = init["upload_id"]; r2key = init["r2_key"]
        total = init["total_parts"]; psize = init["part_size"]
        urls = {int(k): v for k, v in (init.get("initial_urls") or {}).items()}
        etags = {}
        def have_all():
            return len(etags) == total and all(u is not None for u in urls.values())
        partno = 1
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            futs = {}
            while len(etags) < total:
                # request URLs for parts not yet fetched
                need = [p for p in range(1, total + 1)
                        if p not in etags and p not in urls and p not in futs]
                if need:
                    got = api("/upload/parts", {"upload_id": upload_id, "part_numbers": need[:110]})
                    for pu in got.get("part_urls", []):
                        urls[pu["partNumber"]] = pu["url"]
                ready = [p for p in range(1, total + 1) if p in urls and p not in etags and p not in futs]
                for p in ready:
                    start = (p - 1) * psize
                    chunk = fp + f".part{p}"
                    if not os.path.exists(chunk):
                        with open(fp, "rb") as f:
                            f.seek(start)
                            data = f.read(psize)
                        with open(chunk, "wb") as cf2: cf2.write(data)
                    futs[p] = ex.submit(put_part, urls[p], chunk)
                    if len(futs) - len(etags) >= 12: break
                done = [p for p, fu in futs.items() if p not in etags and fu.done()]
                for p in done:
                    et = futs[p].result()
                    if et: etags[p] = et; os.remove(fp + f".part{p}")
                    else: del futs[p]
                    print(f"  part {p}/{total} ok" if et else f"  part {p} FAILED", flush=True)
                if not done: time.sleep(1)
        cmp = api("/upload/complete-multipart",
                  {"upload_id": upload_id, "parts": [{"partNumber": p, "etag": e} for p, e in sorted(etags.items())]})
        print("complete:", cmp, flush=True)
        assert cmp.get("success"), "multipart complete failed"
    conf = api("/upload/confirm", {"filename": os.path.basename(fp), "size": size,
                                   "content_type": ct, "r2_key": r2key})
    print("CONFIRM:", json.dumps(conf, indent=1), flush=True)
    if conf.get("success"):
        json.dump({"file": conf["file"], "owner_token": conf.get("owner_token")},
                  open(fp + ".storageto.json", "w"))

if __name__ == "__main__":
    main()
