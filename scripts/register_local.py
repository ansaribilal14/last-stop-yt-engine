#!/usr/bin/env python3
"""register_local.py — gate + register a manually-obtained cache file.
Usage: python3 scripts/register_local.py <slug> <key> [path]
Runs the face-content gate on an existing ytdl_cache file and, if it passes
(strong/weak), writes the ok entry into download_state.json. Never downloads.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mirror_dl import content_gate, load_faceapp, probe_dur  # noqa: E402

ROOT = "/home/z/my-project/engine/projects"


def main():
    slug, key = sys.argv[1], sys.argv[2]
    base = f"{ROOT}/{slug}"
    path = sys.argv[3] if len(sys.argv) > 3 else f"{base}/ytdl_cache/{key}.mp4"
    if not os.path.exists(path):
        print(f"[register] MISSING {path}")
        return 1
    app, cents = load_faceapp()

    def log(m):
        print(m, flush=True)

    verdict, ah, best = content_gate(path, app, cents, key, log)
    if verdict not in ("strong", "weak"):
        print(f"[register] REJECT verdict={verdict} — delete {path} if wrong content")
        return 1
    d = probe_dur(path)
    spath = f"{base}/download_state.json"
    state = json.load(open(spath))
    state[key] = {"status": "ok", "dur": round(d, 1), "mirror": "local-manual",
                  "title": os.path.basename(path), "ah_present": ah, "verify": verdict}
    json.dump(state, open(spath, "w"), indent=1)
    print(f"[register] OK {key} dur={d:.0f}s verdict={verdict} ah={ah}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
