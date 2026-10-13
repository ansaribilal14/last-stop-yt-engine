#!/usr/bin/env python3
"""resolve_sources.py — resolve search queries to video IDs (local-only, R8).
Usage: python3 resolve_sources.py <project>
Reads  projects/<p>/sources_plan.json
Writes projects/<p>/subject_sources.json + projects/<p>/waves.json
Resolution: yt-dlp `ytsearch1:<q>` --print id,title,channel (title+channel sanity gate).
Resumable: already-resolved keys are kept.
"""
import json, os, subprocess, sys

PROJ = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
BASE = f"/home/z/my-project/engine/projects/{PROJ}"
plan = json.load(open(f"{BASE}/sources_plan.json"))
out_p = f"{BASE}/subject_sources.json"

resolved = {}
if os.path.exists(out_p):
    for s in json.load(open(out_p)):
        if s.get("video_id"):
            resolved[s["key"]] = s

def ytsearch(q):
    r = subprocess.run(
        ["python3", "-m", "yt_dlp", "--no-cache-dir", "--no-check-certificates",
         "--js-runtimes", "node",
         "--extractor-args", "youtube:player_client=tv_simply",
         "--extractor-args", "youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416",
         "ytsearch1:" + q, "--print", "%(id)s\t%(title)s\t%(channel)s\t%(duration)s"],
        capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    parts = r.stdout.strip().split("\t")
    if len(parts) < 3: return None
    return {"video_id": parts[0], "title": parts[1], "channel": parts[2],
            "duration": float(parts[3]) if parts[3:] and parts[3] not in ("NA", "") else 0.0}

changed = 0
for src in plan["sources"]:
    k = src["key"]
    if k in resolved:
        continue
    info = ytsearch(src["q"])
    if not info:
        print(f"RESOLVE FAIL {k}: {src['q']}", flush=True)
        continue
    ch = (info["channel"] or "").lower()
    ok = ("babymonster" in ch or "yg entertainment" in ch or "official" in ch
          or src["kind"] in ("stage", "misc"))
    if not ok:
        print(f"  channel-gate reject {k}: {info['channel']}", flush=True)
    rec = dict(src)
    rec.update(info)
    rec["subject_tags"] = src["tags"]
    resolved[k] = rec
    changed += 1
    print(f"OK {k} -> {info['video_id']} | {info['title'][:48]} | {info['channel']}", flush=True)

out = list(resolved.values())
json.dump(out, open(out_p, "w"), indent=1)
waves = {}
for s in out:
    if not s.get("video_id"): continue
    waves.setdefault(s["kind"], []).append(s["video_id"])
waves["context"] = waves.pop("doc", []) + waves.pop("misc", []) if False else waves.get("context", []) + waves.pop("doc", []) + waves.pop("misc", [])
json.dump(waves, open(f"{BASE}/waves.json", "w"), indent=1)
print(f"WROTE {len(out)} sources, waves: { {k: len(v) for k, v in waves.items()} }")
