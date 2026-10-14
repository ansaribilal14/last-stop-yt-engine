#!/usr/bin/env python3
"""final_crf18.py — re-encode ahyeon final video to CRF18 in 3 resumable parts.
Usage: python3 final_crf18.py <part:1|2|3|concat|all>
Splits at segment boundaries (keyframe-exact). Audio = same linear loudnorm chain
(same measured constants -> identical gain across parts -> seamless concat).
"""
import json, os, subprocess, sys

BASE = "/home/z/my-project/engine/projects/ahyeon"
RENDER = f"{BASE}/render"
FPS = 30
tl = json.load(open(f"{RENDER}/timeline.json"))
N = len(tl)
P = 6
BOUNDS = [round(N * k / P) for k in range(P + 1)]   # 6 parts by segment index
meas = json.load(open(f"{RENDER}/loudnorm.json"))
AF = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true"
      f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
      f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}")

def write_concat(i0, i1, path):
    with open(path, "w") as f:
        for t in tl[i0:i1]:
            f.write(f"file '{RENDER}/seg_{t['id']}.mp4'\n")

def encode_part(p):
    i0, i1 = BOUNDS[p - 1], BOUNDS[p]
    txt = f"{RENDER}/part{p}.txt"
    out = f"{RENDER}/p{p}.mp4"
    write_concat(i0, i1, txt)
    want = sum(t["dur"] for t in tl[i0:i1])
    if os.path.exists(out) and abs(_dur(out) - want) < 0.2:
        print(f"part{p} already done")
    else:
        start = tl[i0]["start"]
        cmd = ["ffmpeg", "-y", "-nostdin", "-f", "concat", "-safe", "0", "-i", txt,
               "-ss", f"{start:.4f}", "-i", f"{RENDER}/mix.wav",
               "-filter_complex", f"[1:a]{AF}[outa]",
               "-map", "0:v", "-map", "[outa]",
               "-t", f"{want:.4f}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
               "-profile:v", "high", "-level", "4.0", "-pix_fmt", "yuv420p",
               "-r", str(FPS), "-video_track_timescale", "15360",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-500:])
        if abs(_dur(out) - want) >= 0.2:
            os.remove(out); raise RuntimeError(f"part{p} duration mismatch, retry")
        print(f"part{p}: {i1-i0} segs, {_dur(out):.1f}s, {os.path.getsize(out)//1000000}MB")
    # verified -> free its source segments (disk budget)
    for t in tl[i0:i1]:
        sp = f"{RENDER}/seg_{t['id']}.mp4"
        if os.path.exists(sp): os.remove(sp)

def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except Exception: return -1.0

def concat():
    with open(f"{RENDER}/parts.txt", "w") as f:
        for p in range(1, P + 1):
            f.write(f"file '{RENDER}/p{p}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-nostdin", "-f", "concat", "-safe", "0",
                    "-i", f"{RENDER}/parts.txt", "-c", "copy",
                    "-movflags", "+faststart", f"{BASE}/final.mp4"], check=True,
                   capture_output=True, text=True)
    print(f"final.mp4: {_dur(f'{BASE}/final.mp4'):.3f}s {os.path.getsize(f'{BASE}/final.mp4')//1000000}MB")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "concat": concat()
    else:
        parts = [1, 2, 3] if mode == "all" else [int(mode)]
        for p in parts: encode_part(p)
        if mode == "all" or mode == "concat":
            if all(os.path.exists(f"{RENDER}/p{p}.mp4") for p in range(1, P + 1)):
                concat()
