#!/usr/bin/env python3
"""verify_one.py — run the content gate on one already-downloaded file and
commit it to download_state.json. Usage: verify_one.py <key> [mirror_label]"""
import json, sys
sys.path.insert(0, "/home/z/my-project/engine/scripts")
from mirror_dl import load_faceapp, content_gate, probe_dur

def main():
    key = sys.argv[1]
    mirror = sys.argv[2] if len(sys.argv) > 2 else "manual"
    base = "/home/z/my-project/engine/projects/ahyeon"
    out = f"{base}/ytdl_cache/{key}.mp4"
    d = probe_dur(out)
    if d <= 0:
        print(f"[{key}] no/probe-fail file"); return
    app, cents = load_faceapp()
    verdict, ah, best = content_gate(out, app, cents, key, lambda m: print(m, flush=True))
    state = json.load(open(f"{base}/download_state.json"))
    if verdict in ("strong", "weak"):
        state[key] = {"status": "ok", "dur": round(d, 1), "mirror": mirror,
                      "title": None, "ah_present": ah, "verify": verdict, "faces_ok": True}
        print(f"[{key}] ACCEPT {verdict} dur={d:.0f}s ah={ah}")
    else:
        print(f"[{key}] REJECT {verdict} — removing")
        import os; os.remove(out)
        state[key] = {"status": "failed", "fails": 99, "tries": "manual-verify"}
    json.dump(state, open(f"{base}/download_state.json", "w"), indent=1)

if __name__ == "__main__":
    main()
