#!/usr/bin/env python3
"""faceverify.py v3 — 'character edge': per-shot Ahyeon-presence scoring.
Batched per-source + SEGMENTED for long files: sources are processed in
<=320s temporal segments; each segment's results persist to a sidecar
(sec_scores_<label>_<seg>.json) so timeouts never lose work. Merge-on-write
into shots_index.json after each segment. Single-flight lock.
Usage: python3 faceverify.py <project> [--segment 320]
"""
import json, os, subprocess, sys, glob, tempfile, fcntl
import numpy as np

BASE_ROOT = "/home/z/my-project/engine/projects"
REFS = "/home/z/my-project/engine/tools/cce_references"
SEG_DEFAULT = 320  # seconds of source per work unit


def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    seg_len = SEG_DEFAULT
    if "--segment" in sys.argv:
        seg_len = float(sys.argv[sys.argv.index("--segment") + 1])

    base = f"{BASE_ROOT}/{proj}"
    idx_p = f"{base}/shots_index.json"
    lock_f = open(f"{base}/.faceverify.lock", "w")
    try:
        fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("[faceverify] another instance holds the lock — exiting", flush=True)
        return
    os.makedirs(f"{base}/fv_cache", exist_ok=True)

    from insightface.app import FaceAnalysis
    # landmark/genderage models cost more than det+rec combined (1k3d68 = 143MB
    # per face) — scoring only needs detection + recognition
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"],
                       providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(320, 320))
    import cv2

    summ = json.load(open(f"{REFS}/refs_summary.json"))
    cents = {m: np.array(v["centroid"], dtype=np.float32)
             for m, v in summ["members"].items()}

    idx = json.load(open(idx_p))

    # build work units: (label, seg_idx, t0, t1, shots_inside)
    units = []
    for label, entry in sorted(idx.items()):
        shots = entry["shots"]
        dur = max(s["end"] for s in shots)
        nseg = max(1, int(dur / seg_len + 0.999))
        for si in range(nseg):
            a, b = si * seg_len, min((si + 1) * seg_len, dur)
            inside = [s for s in shots
                      if "ah_score" not in s
                      and a <= (s["start"] + s["dur"] / 2) < b + 0.001]
            if inside:
                units.append((label, si, a, b, inside))
    total_pending = sum(len(u[4]) for u in units)
    print(f"[faceverify] {len(units)} segment units, {total_pending} shots pending", flush=True)

    for label, si, a, b, shots in units:
        entry = idx[label]
        sidecar_p = f"{base}/fv_cache/sec_{label}_{si}.json"
        sidecar = json.load(open(sidecar_p)) if os.path.exists(sidecar_p) else {}
        src = entry["shots"][0]["src"]
        if not os.path.isabs(src):
            src = f"{base}/{src}"
        if not os.path.exists(src):
            print(f"[{label}] MISSING src", flush=True)
            for s in shots: s["ah_score"] = 0.0
            continue
        avg_dur = (b - a) / max(1, len([s for s in entry["shots"]
                                        if a <= s["start"] < b]))
        s_fps = 1.0 if avg_dur < 4 else (0.5 if avg_dur < 8 else 0.33)
        with tempfile.TemporaryDirectory(prefix=f"fv_") as td:
            subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}",
                            "-i", src, "-vf", f"fps={s_fps},scale='min(640,iw)':-2",
                            "-q:v", "5", f"{td}/f%05d.jpg"],
                           capture_output=True, timeout=300)
            frames = sorted(glob.glob(f"{td}/f*.jpg"))
            sec_scores = {}
            for i, fp in enumerate(frames):
                sec = a + int(i / s_fps)
                if str(sec) in sidecar:
                    sec_scores[sec] = tuple(sidecar[str(sec)])
                    continue
                img = cv2.imread(fp)
                if img is None: continue
                faces = app.get(img)
                if not faces: continue
                big = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                if (big.bbox[2] - big.bbox[0]) < 28: continue
                emb = big.normed_embedding.astype(np.float32)
                best, best_ah = -1.0, -1.0
                for m, c in cents.items():
                    s_ = float(np.dot(emb, c))
                    if s_ > best: best = s_
                    if m == "ahyeon": best_ah = s_
                sec_scores[sec] = (best, best_ah, "")
            # persist sidecar (checkpoint — kill-safe)
            json.dump({str(k): v for k, v in sec_scores.items()},
                      open(sidecar_p + ".tmp", "w"))
            os.replace(sidecar_p + ".tmp", sidecar_p)
            # map shots -> scores
            for s in shots:
                probes = [s["start"] + s["dur"] * f for f in (0.3, 0.55, 0.8)]
                best_ah = -1.0
                for t in probes:
                    for sec in (int(t), int(t) + 1):
                        rec = sec_scores.get(sec)
                        if rec and rec[1] > best_ah:
                            best_ah = rec[1]
                if best_ah >= 0:
                    s["ah_score"] = round(best_ah, 4)
                else:
                    s["ah_score"] = 0.0
                    s["ah_unsampled"] = True
        # merge-on-write into index (atomic)
        disk = json.load(open(idx_p))
        new_scores = {s["start"]: s.get("ah_score") for s in shots}
        new_flags = {s["start"]: s.get("ah_unsampled") for s in shots}
        for ds in disk.get(label, {}).get("shots", []):
            if ds["start"] in new_scores:
                ds["ah_score"] = new_scores[ds["start"]]
                if new_flags.get(ds["start"]): ds["ah_unsampled"] = True
        tmp = idx_p + ".tmp"
        json.dump(disk, open(tmp, "w"), indent=1)
        os.replace(tmp, idx_p)
        n_done = sum(1 for e in disk.values() for s in e["shots"] if "ah_score" in s)
        print(f"[{label}#{si}] {a:.0f}-{b:.0f}s scored (+{len(shots)}) | total {n_done}/{sum(e['n_shots'] for e in disk.values())}", flush=True)

    n_done = sum(1 for e in idx.values() for s in e["shots"] if "ah_score" in s)
    n_all = sum(e["n_shots"] for e in idx.values())
    print(f"FACEVERIFY: {n_done}/{n_all} shots scored", flush=True)


if __name__ == "__main__":
    main()
