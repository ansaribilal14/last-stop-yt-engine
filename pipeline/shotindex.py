#!/usr/bin/env python3
"""shotindex.py — shot-level footage indexer (T5).
For every source video in projects/<slug>/ytdl_cache/:
  1. Detect shot boundaries with ffmpeg scdet (zero-dep, 7x faster than PySceneDetect,
     identical accuracy per T8-b benchmark).
  2. Measure per-shot motion energy (RMS frame diff) + brightness + duration.
  3. Emit shots_index.json: [{src, label, start, end, dur, motion, section_hint, tags}]
  4. Emit contact sheets per source: render/storyboard/src_<label>.jpg (5x4 tile grid).

Deterministic: same sources -> same index. Resume-safe (skips indexed sources).
Usage: python3 shotindex.py <project> [--force]
"""
import json, os, subprocess, sys

BASE_ROOT = "/home/z/my-project/engine/projects"

def sh(args, timeout=300):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return r

def probe_dur(src):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", src])
    try: return float(r.stdout.strip())
    except Exception: return -1.0

def detect_shots(src, dur):
    """scdet thresholds -> list of (start, end, score). Downscaled luma-only scan."""
    # 1) boundary timestamps — output pairs: "frame:N pts:... pts_time:T" then
    #    "lavfi.scene_score=S" (select passes frames above threshold)
    r = sh(["ffmpeg", "-nostdin", "-i", src, "-vf",
            "select='gt(scene,0.28)',metadata=print:file=-", "-an",
            "-f", "null", "-"], timeout=420)
    pts = []
    for ln in r.stdout.splitlines():
        if "pts_time:" in ln:
            try: pts.append(float(ln.split("pts_time:")[1].split()[0]))
            except Exception: pass
    # 2) motion energy: frame-diff proxy via signalstats YDIF average per 1s bucket
    r2 = sh(["ffmpeg", "-nostdin", "-i", src, "-vf",
             "scale=160:90,signalstats,metadata=print:key=lavfi.signalstats.YDIF:file=-",
             "-an", "-f", "null", "-"], timeout=420)
    ydif = {}
    cur_t = None
    for ln in r2.stdout.splitlines():
        if "pts_time:" in ln:
            try: cur_t = float(ln.split("pts_time:")[1].split()[0])
            except Exception: cur_t = None
        elif cur_t is not None and "YDIF=" in ln:
            try: ydif[int(cur_t)] = float(ln.split("YDIF=")[1].split()[0])
            except Exception: pass
    # build shots
    bounds = [0.0] + [p for p in pts if 0.3 < p < dur - 0.3] + [dur]
    shots = []
    MIN_SHOT = 1.2
    for a, b in zip(bounds, bounds[1:]):
        if b - a < MIN_SHOT:
            if shots:  # merge tiny shot into previous
                shots[-1] = (shots[-1][0], b)
            continue
        shots.append((a, b))
    out = []
    for a, b in shots:
        e = [ydif.get(int(t), 0.0) for t in range(int(a), min(int(b) + 1, int(dur)))]
        motion = sum(e) / max(1, len(e))
        out.append({"start": round(a, 2), "end": round(b, 2),
                    "dur": round(b - a, 2), "motion": round(motion, 3)})
    return out

def section_hint(t, dur):
    """Rough MV structure hint by relative position (Director refines)."""
    f = t / max(dur, 1.0)
    if f < 0.12: return "intro"
    if f < 0.30: return "verse1"
    if f < 0.45: return "chorus1"
    if f < 0.58: return "verse2"
    if f < 0.72: return "chorus2"
    if f < 0.85: return "bridge"
    return "final_chorus"

def contact_sheet(src, label, outdir, n=20):
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/src_{label}.jpg"
    if os.path.exists(out): return out
    r = sh(["ffmpeg", "-y", "-nostdin", "-i", src, "-vf",
            f"fps=1/{max(4, int(probe_dur(src) or 240) // n)},scale=320:180,tile={n//4}x4",
            "-frames:v", "1", "-q:v", "5", out], timeout=240)
    return out if r.returncode == 0 else None

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    force = "--force" in sys.argv
    base = f"{BASE_ROOT}/{proj}"
    cache = f"{base}/ytdl_cache"
    render = f"{base}/render"
    idx_p = f"{base}/shots_index.json"
    sources = {s["video_id"]: s for s in json.load(open(f"{base}/subject_sources.json"))}
    idx = {}
    if os.path.exists(idx_p) and not force:
        idx = json.load(open(idx_p))
    files = sorted(f for f in os.listdir(cache) if f.endswith(".mp4"))
    for f in files:
        label = f[:-4]
        if label in idx and not force:
            continue
        src = f"{cache}/{f}"
        dur = probe_dur(src)
        if dur <= 0:
            print(f"[{label}] probe fail, skip"); continue
        shots = detect_shots(src, dur)
        for s in shots:
            s["section_hint"] = section_hint(s["start"] + s["dur"] / 2, dur)
            s["label"] = label
            s["tags"] = sources.get(label, {}).get("subject_tags", [])
            s["src"] = f"ytdl_cache/{f}"
        idx[label] = {"dur": round(dur, 2), "n_shots": len(shots), "shots": shots}
        cs = contact_sheet(src, label, f"{render}/storyboard")
        print(f"[{label}] {dur:.0f}s -> {len(shots)} shots (sheet: {bool(cs)})", flush=True)
        json.dump(idx, open(idx_p, "w"), indent=1)  # incremental persist
    n_shots = sum(v["n_shots"] for v in idx.values())
    print(f"INDEX: {len(idx)} sources, {n_shots} shots -> {idx_p}")

if __name__ == "__main__":
    main()
