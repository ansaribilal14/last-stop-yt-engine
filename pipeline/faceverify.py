#!/usr/bin/env python3
"""faceverify.py — 'character edge': per-shot Ahyeon-presence scoring (T5 enrichment).
Uses character-clip-extractor's committed face centroid (references/refs_summary.json)
+ InsightFace buffalo_l. Samples N frames per shot, max cosine vs centroid -> ah_score.
Enriches shots_index.json in place (resume-safe).
Usage: python3 faceverify.py <project> [--frames 2] [--limit N]
"""
import json, os, subprocess, sys
import numpy as np

BASE_ROOT = "/home/z/my-project/engine/projects"
REFS = "/home/z/my-project/engine/tools/cce_references"

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    frames_n = 2
    if "--frames" in sys.argv: frames_n = int(sys.argv[sys.argv.index("--frames") + 1])
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 99999

    base = f"{BASE_ROOT}/{proj}"
    idx_p = f"{base}/shots_index.json"
    idx = json.load(open(idx_p))
    summ = json.load(open(f"{REFS}/refs_summary.json"))
    cent = np.array(summ["members"]["ahyeon"]["centroid"], dtype=np.float32)

    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(320, 320))

    done = 0
    for label, entry in sorted(idx.items()):
        src = f"{base}/{entry['shots'][0]['src']}"
        need = [s for s in entry["shots"] if "ah_score" not in s]
        if not need: continue
        for s in need:
            mid = s["start"] + s["dur"] / 2
            ts = [s["start"] + s["dur"] * 0.35, mid, s["start"] + s["dur"] * 0.75][:frames_n]
            best = -1.0
            for t in ts:
                # extract frame at 480px width
                r = subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{t:.2f}", "-i", src,
                                    "-frames:v", "1", "-vf", "scale=480:-2", "-f", "image2pipe",
                                    "-vcodec", "png", "-"], capture_output=True, timeout=60)
                if r.returncode != 0 or not r.stdout: continue
                arr = np.frombuffer(r.stdout, np.uint8)
                img = cv_imdecode(arr)
                if img is None: continue
                faces = app.get(img)
                for f in faces:
                    c = float(np.dot(f.normed_embedding.astype(np.float32), cent))
                    if c > best: best = c
            s["ah_score"] = round(max(0.0, best), 4)
            done += 1
            if done % 20 == 0:
                json.dump(idx, open(idx_p, "w"), indent=1)
                print(f"[{label}] {s['start']:.0f}s ah={s['ah_score']:.2f} ({done} shots)", flush=True)
            if done >= limit: break
        json.dump(idx, open(idx_p, "w"), indent=1)
        if done >= limit: break
    n_scored = sum(1 for e in idx.values() for s in e["shots"] if "ah_score" in s)
    n_all = sum(e["n_shots"] for e in idx.values())
    print(f"FACEVERIFY: {n_scored}/{n_all} shots scored")

def cv_imdecode(buf):
    import cv2
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)

if __name__ == "__main__":
    main()
