#!/usr/bin/env python3
"""assemble.py — render pipeline for 'Why there will be no next BLACKPINK'
Stages: plan | segments | audio | final   (each resumable)
Output: projects/blackpink/render/
Spec: 1920x1080 30fps H.264 CRF16, AAC 192k 48kHz stereo, -14 LUFS, 2040.0s exact.
"""
import json, math, os, random, subprocess, sys, wave

BASE = "/home/z/my-project/engine/projects/blackpink"
CLIPS = f"{BASE}/clips"; NARR = f"{BASE}/narration"; RENDER = f"{BASE}/render"
FPS = 30; TOTAL = 2040.0
GOLD = "c9a84c"; CREAM = "f5f2ea"
FONT_B = "/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Medium.ttf"
ENC = ["-c:v","libx264","-preset","veryfast","-crf","16","-profile:v","high",
       "-level","4.0","-pix_fmt","yuv420p","-r",str(FPS),"-video_track_timescale","15360"]

def sh(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"CMD FAIL: {' '.join(args[:6])}...\n{r.stderr[-800:]}")
    return r

def syspath():
    sys.path.insert(0, "/home/z/my-project/engine/pipeline")
    from script_beats import BEATS
    return BEATS

def pool_for(beat, sources, rnd):
    pool = []
    for v in beat.get("vids", []):
        pool += sorted([f"{CLIPS}/{f}" for f in os.listdir(CLIPS)
                        if f.startswith(f"seg_{v}_") and f.endswith(".mp4")])
    if len(pool) < 3:  # widen to tag pool
        for t in beat.get("tags", []):
            for v, meta in sources.items():
                if t in meta["subject_tags"]:
                    pool += sorted([f"{CLIPS}/{f}" for f in os.listdir(CLIPS)
                                    if f.startswith(f"seg_{v}_") and f.endswith(".mp4")])
    if len(pool) < 3:  # global fallback: group MV/stage footage
        for v, meta in sources.items():
            if "blackpink" in meta["subject_tags"]:
                pool += sorted([f"{CLIPS}/{f}" for f in os.listdir(CLIPS)
                                if f.startswith(f"seg_{v}_") and f.endswith(".mp4")])
    rnd.shuffle(pool)
    return pool

def stage_plan():
    BEATS = syspath()
    timing = json.load(open(f"{NARR}/timing.json"))
    sources = {s["video_id"]: s for s in json.load(open(f"{BASE}/subject_sources.json"))}
    rnd = random.Random(20160808)
    target = {"title":18.0,"chapter":16.0,"stat":12.0,"close":20.0}
    tl, used, pools = [], set(), {}
    for b in BEATS:
        vd = timing.get(b["id"], {}).get("dur", 0.0)
        kind = b["kind"]; slot = vd + 0.8
        if kind == "card":
            ck = b["card"]["kind"]
            slot = vd + target.get(ck, 16.0)
            if ck == "credits": slot = vd + 50.0
        elif not b["text"].strip():        # interlude
            slot = 30.0
        else:                              # clips beat with narration
            slot = vd + 7.0
        n = max(1, math.ceil(slot / 9.5)) if kind == "clips" else (2 if kind == "card" else 0)
        picks = []
        if n:
            key = tuple(b.get("vids", [])) or ("tags", tuple(b.get("tags", [])))
            if key not in pools: pools[key] = pool_for(b, sources, rnd)
            pool = [c for c in pools[key] if c not in used] or pools[key]
            picks = (pool * math.ceil(n / max(1, len(pool))))[:n]
            used.update(picks)
        tl.append({"id": b["id"], "kind": kind, "card": b.get("card"),
                   "voice": vd, "slot": round(slot, 4), "clips": picks})
    # frame-accurate normalization to exactly TOTAL
    rem = TOTAL - sum(t["slot"] for t in tl)
    add = rem / len(tl)
    for t in tl: t["slot"] = round(t["slot"] + add, 4)
    frames = [round(t["slot"] * FPS) for t in tl]
    frames[-1] += FPS * round(TOTAL) - sum(frames)   # exact 61200
    for t, f in zip(tl, frames):
        t["frames"] = f; t["dur"] = round(f / FPS, 6)
    # cumulative offsets (voice starts 0.8s into its segment)
    off = 0.0
    for t in tl:
        t["start"] = round(off, 4); t["voice_at"] = round(off + 0.8, 4)
        off += t["dur"]
    tl[-1]["end"] = TOTAL
    json.dump(tl, open(f"{RENDER}/timeline.json", "w"), indent=1)
    print(f"plan: {len(tl)} beats, sum={sum(t['dur'] for t in tl):.3f}s, "
          f"clips assigned={sum(len(t['clips']) for t in tl)}")

def drawtext(txt, font, size, color, y, box=False):
    tf = f"{RENDER}/txt_{abs(hash((txt,size,color,y)))%10**8}.txt"
    with open(tf, "w") as f: f.write(txt)
    e = f"drawtext=fontfile={font}:textfile={tf}:fontsize={size}:fontcolor={color}:x=(w-text_w)/2:y={y}"
    if box: e += ":box=1:boxcolor=0x0a0a0aB3:boxborderw=18"
    return e

def card_filter(t):
    lines = t["card"].get("lines", []); ck = t["card"]["kind"]; d = t["dur"]
    bg_in = bool(t.get("clips")) and os.path.exists(t["clips"][0])
    fc = []
    if bg_in:
        fc.append(f"[0:v]scale=1920:1080:flags=lanczos,fps={FPS},boxblur=24:2,"
                  f"eq=brightness=-0.18:saturation=0.55,format=yuv420p[bg]")
    else:
        fc.append(f"color=c=0x0a0a0a:s=1920x1080:r={FPS}:d={d:.4f}[bg]")
    texts = []; rule_y = None
    if ck == "chapter":
        texts.append(drawtext(" ".join(t["card"]["num"]), FONT_M, 40, f"0x{GOLD}@0.95", "h/2-190"))
        texts.append(drawtext(t["card"]["title"], FONT_B, 92, f"0x{CREAM}", "h/2-96"))
        rule_y = "h/2+46"
    elif ck == "title":
        texts.append(drawtext(lines[0], FONT_B, 96, f"0x{CREAM}", "h/2-190"))
        texts.append(drawtext(lines[1], FONT_B, 96, f"0x{GOLD}", "h/2-70"))
        rule_y = "h/2+72"
    elif ck == "stat":
        texts.append(drawtext(t["card"]["big"], FONT_B, 150, f"0x{GOLD}", "h/2-150"))
        texts.append(drawtext(t["card"]["small"], FONT_M, 38, f"0x{CREAM}@0.9", "h/2+40"))
    elif ck == "close":
        texts.append(drawtext(lines[0], FONT_B, 84, f"0x{GOLD}", "h/2-170"))
        texts.append(drawtext(lines[1], FONT_B, 84, f"0x{CREAM}", "h/2-60"))
        texts.append(drawtext(lines[2], FONT_B, 84, f"0x{CREAM}", "h/2+50"))
    elif ck == "credits":
        for i, ln in enumerate(lines):
            texts.append(drawtext(ln, FONT_M, 34, f"0x{CREAM}@0.85", f"h/2-140+{i*64}"))
    cur = "bg"
    for i, e in enumerate(texts):
        fc.append(f"[{cur}]{e}[p{i}]"); cur = f"p{i}"
    if rule_y:
        fc.append(f"[{cur}]drawbox=x=900:y={rule_y}:w=120:h=3:color=0x{GOLD}@0.85:t=fill[rule]")
        cur = "rule"
    fc.append(f"[{cur}]fade=t=in:st=0:d=0.8,fade=t=out:st={max(0.1,d-0.9)}:d=0.9[vout]")
    return ";".join(fc), "vout"

def stage_segments():
    tl = json.load(open(f"{RENDER}/timeline.json"))
    os.makedirs(RENDER, exist_ok=True)
    fallback = f"{CLIPS}/seg_IHNzOHi8sJs_00_00010.mp4"
    for i, t in enumerate(tl):
        out = f"{RENDER}/seg_{t['id']}.mp4"
        if os.path.exists(out) and abs(_dur(out) - t["dur"]) < 0.05:
            continue
        d = t["dur"]
        if t["kind"] == "card" and t["clips"]:
            # backdrop card: blur + darken one clip, overlay typography
            src = t["clips"][0] if os.path.exists(t["clips"][0]) else fallback
            cf, _ = card_filter(t)
            cmd = ["ffmpeg","-y","-nostdin","-stream_loop","-1","-i",src,
                   "-filter_complex",cf,"-map","[vout]","-t",f"{d:.4f}"] + ENC + [out]
        elif t["kind"] == "card":
            # solid-color card (no backdrop)
            cf, _ = card_filter(t)
            cmd = ["ffmpeg","-y","-nostdin","-f","lavfi","-i",
                   f"color=c=0x0a0a0a:s=1920x1080:r={FPS}:d={d:.4f}",
                   "-filter_complex",cf,"-map","[vout]","-t",f"{d:.4f}"] + ENC + [out]
        else:
            # clips beat (montage or interlude)
            picks = [c for c in t["clips"] if os.path.exists(c)] or [fallback]
            n = len(picks); per = d / n
            cmd = ["ffmpeg","-y","-nostdin"]
            for c in picks: cmd += ["-stream_loop","-1","-i",c]
            fc = [f"[{j}:v]scale=1920:1080:flags=lanczos,fps={FPS},setsar=1,"
                  f"format=yuv420p,trim=duration={per:.4f},setpts=PTS-STARTPTS[c{j}]"
                  for j in range(n)]
            chain = "".join(f"[c{j}]" for j in range(n)) + f"concat=n={n}:v=1:a=0"
            if i == 0: chain += ",fade=t=in:st=0:d=1.2"
            if t["id"] == tl[-1]["id"]: chain += f",fade=t=out:st={max(0.1,d-2.0)}:d=2.0"
            fc.append(chain + "[vout]")
            cmd += ["-filter_complex",";".join(fc),"-map","[vout]",
                    "-t",f"{d:.4f}"] + ENC + [out]
        sh(cmd)
        print(f"[{i+1}/{len(tl)}] {t['id']} {d:.1f}s ok", flush=True)

def _dur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except Exception: return -1.0

def stage_audio():
    tl = json.load(open(f"{RENDER}/timeline.json"))
    SR = 48000; N = int(TOTAL * SR)
    os.makedirs(f"{RENDER}/wav", exist_ok=True)
    # decode narration to mono 48k wavs
    for t in tl:
        if t["voice"] > 0:
            src = f"{NARR}/{t['id']}.mp3"; dst = f"{RENDER}/wav/{t['id']}.wav"
            if not os.path.exists(dst):
                sh(["ffmpeg","-y","-nostdin","-i",src,"-ar",str(SR),"-ac","1",
                    "-c:a","pcm_s16le",dst])
    import numpy as np
    voice = np.zeros(N, dtype=np.float32)
    for t in tl:
        if t["voice"] > 0:
            with wave.open(f"{RENDER}/wav/{t['id']}.wav") as w:
                data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
            start = int(t["voice_at"] * SR)
            end = min(N, start + len(data))
            voice[start:end] += data[:end - start].astype(np.float32) / 32768.0
    # ambient bed: layered drone + slow swell, gated by voice envelope
    rng = np.random.default_rng(7)
    bed = np.zeros(N, dtype=np.float32)
    CH = SR * 30
    env = np.abs(voice)
    k = int(0.35 * SR)
    cs = np.cumsum(env, dtype=np.float32)
    ma = ((cs[k:] - cs[:-k]) / k) if len(cs) > k else env[:1]
    ma = np.minimum(1.0, ma * 14.0)
    gate = 0.16 + 0.84 * (1.0 - np.clip(ma, 0, 1))   # quiet under voice
    lead = np.full(min(k, N), gate[0] if len(gate) else 1.0, dtype=np.float32)
    gate = np.concatenate((lead, gate.astype(np.float32)))
    if len(gate) < N: gate = np.pad(gate, (0, N - len(gate)), constant_values=1.0)
    gate = gate[:N]
    t0 = 0
    while t0 < N:
        n = min(CH, N - t0); tt = (np.arange(t0, t0 + n) / SR).astype(np.float32)
        seg = (0.30*np.sin(2*np.pi*55*tt) + 0.22*np.sin(2*np.pi*110.3*tt + 1.1)
               + 0.14*np.sin(2*np.pi*164.6*tt + 2.3) + 0.10*np.sin(2*np.pi*220.6*tt + 0.4))
        seg *= (0.62 + 0.38*np.sin(2*np.pi*tt/47.0 + 0.9))       # slow swell
        seg += 0.05 * rng.standard_normal(n).astype(np.float32) * 0.5
        bed[t0:t0+n] = seg; t0 += n
    mix = voice + bed * gate * 0.30
    del voice, bed, gate, env, cs
    peak = float(np.max(np.abs(mix)));  mix *= (0.72 / max(peak, 1e-6))
    import gc; gc.collect()
    with wave.open(f"{RENDER}/mix.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        CH = SR * 60
        for s0 in range(0, N, CH):
            chunk = mix[s0:s0+CH]
            stereo = np.empty((len(chunk), 2), dtype=np.int16)
            stereo[:, 0] = (chunk * 32767.0).astype(np.int16)
            stereo[:, 1] = stereo[:, 0]
            w.writeframes(stereo.tobytes())
    print(f"audio: mix.wav {N/SR:.1f}s written")

def stage_final():
    tl = json.load(open(f"{RENDER}/timeline.json"))
    with open(f"{RENDER}/concat.txt", "w") as f:
        for t in tl: f.write(f"file '{RENDER}/seg_{t['id']}.mp4'\n")
    sh(["ffmpeg","-y","-nostdin","-f","concat","-safe","0","-i",f"{RENDER}/concat.txt",
        "-c","copy",f"{RENDER}/video.mp4"])
    sh(["ffmpeg","-y","-nostdin","-i",f"{RENDER}/video.mp4","-i",f"{RENDER}/mix.wav",
        "-filter_complex","[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[outa]",
        "-map","0:v","-map","[outa]","-c:v","copy",
        "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
        "-movflags","+faststart",f"{BASE}/final.mp4"])
    p = subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_name,width,height,sample_rate,channels",
        "-of","json",f"{BASE}/final.mp4"], capture_output=True, text=True)
    print("QC:", p.stdout)

if __name__ == "__main__":
    os.makedirs(RENDER, exist_ok=True)
    {"plan": stage_plan, "segments": stage_segments,
     "audio": stage_audio, "final": stage_final}[sys.argv[1]]()
