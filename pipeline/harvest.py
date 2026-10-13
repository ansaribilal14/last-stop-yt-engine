#!/usr/bin/env python3
"""harvest.py v3 — energy-window subject clip harvester (R2: sync visuals to subject).
Selects high-energy windows via 8kHz mono RMS, cuts pure-video segments.
Usage: harvest.py plan <cfg.json> | harvest.py run <cfg.json>
cfg: {"out_dir": "...", "jobs": [{"src":..., "label":<video_id>, "tags":[...],
      "n": segments, "seg_len": seconds}]}
Outputs: seg_<label>_<k>_<start>.mp4 + .json sidecar (subject_tags traceability)
"""
import json, os, subprocess, sys

def probe_dur(src):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",src], capture_output=True, text=True)
    return float(r.stdout.strip())

def energy_windows(src, win=0.5):
    """8kHz mono RMS envelope, win seconds per bucket."""
    cmd = ["ffmpeg","-nostdin","-i",src,"-t","600","-vn","-ac","1","-ar","8000",
           "-f","s16le","-"]
    r = subprocess.run(cmd, capture_output=True)
    import numpy as np
    pcm = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    b = int(8000 * win)
    n = len(pcm) // b
    if n == 0: return np.zeros(1, dtype=np.float32)
    return (pcm[:n*b].reshape(n, b) ** 2).mean(axis=1)

def plan_windows(src, n, seg_len, avoid_head=4.0, avoid_tail=4.0, min_gap=6.0):
    dur = probe_dur(src)
    usable = max(0.0, dur - avoid_head - avoid_tail)
    if usable < seg_len: return dur, []
    env = energy_windows(src)
    win = 0.5
    L = int(seg_len / win)
    if len(env) <= L: return dur, []
    import numpy as np
    cs = np.cumsum(np.concatenate(([0.0], env)))
    scores = cs[L:] - cs[:-L]                      # sum energy per seg window
    order = list(range(0, len(scores)))            # windows at 0.5s steps
    order.sort(key=lambda i: -scores[i])
    picked = []
    for i in order:
        t = avoid_head + i * win
        if t + seg_len > dur - avoid_tail: continue
        if all(abs(t - p) >= min_gap for p in picked):
            picked.append(t)
        if len(picked) >= n: break
    picked.sort()
    return dur, picked

def cut(src, out, start, seg_len):
    cmd = ["ffmpeg","-y","-nostdin","-ss",f"{start:.2f}","-t",f"{seg_len:.2f}",
           "-i",src,
           "-vf","scale='min(1280,iw)':-2:flags=lanczos,fps=30,setsar=1,format=yuv420p",
           "-an","-c:v","libx264","-preset","veryfast","-crf","17",
           "-movflags","+faststart", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 50000

def main():
    mode, cfgp = sys.argv[1], sys.argv[2]
    cfg = json.load(open(cfgp))
    out_dir = cfg["out_dir"]; os.makedirs(out_dir, exist_ok=True)
    total = 0
    for job in cfg["jobs"]:
        src, label = job["src"], job["label"]
        if not os.path.exists(src):
            print(f"  skip {label} (no source)"); continue
        n, seg_len = job["n"], job["seg_len"]
        # resumable: count existing segments for this label
        have = len([f for f in os.listdir(out_dir)
                    if f.startswith(f"seg_{label}_") and f.endswith(".mp4")])
        if have >= n:
            total += have; continue
        dur, wins = plan_windows(src, n, seg_len)
        print(f"  {label} {dur:.0f}s, want {n}")
        k = 0
        for start in wins:
            out = f"{out_dir}/seg_{label}_{k:02d}_{int(start):05d}.mp4"
            if os.path.exists(out): k += 1; continue
            if cut(src, out, start, seg_len):
                json.dump({"source": label, "subject_tags": job["tags"],
                           "start": round(start,2), "dur": seg_len},
                          open(out.replace(".mp4",".json"), "w"))
                print(f"    seg{k:02d} @ {start:.0f}s {seg_len}s -> {os.path.basename(out)}")
                k += 1; total += 1
            else:
                print(f"    seg{k:02d} @ {start:.0f}s FAILED")
    print(f"TOTAL: {total}", flush=True)

if __name__ == "__main__":
    main()
