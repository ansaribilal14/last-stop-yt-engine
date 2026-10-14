#!/usr/bin/env python3
"""assemble.py — render pipeline (project-parameterized, resumable)
Stages: plan | segments | audio | final
  python3 assemble.py <stage> [project]     (default project: blackpink)

Audio path (v2 — kills the sine-drone distortion):
  narration (hp+normalized) + composed CC0-sample score (music/score_build.py)
  with opuscar-style ducking (dilate 160ms + smooth 250ms, -9dB under voice),
  chunked lookahead limiter, two-pass LINEAR loudnorm to -14 LUFS.

Spec: 1920x1080 30fps H.264 CRF16, AAC 192k 48kHz stereo, -14 LUFS.
Captions: word-timed ASS burned per segment (edge-tts WordBoundary data).
"""
import json, math, os, random, subprocess, sys, wave

PROJ = "blackpink"
BASE = f"/home/z/my-project/engine/projects/{PROJ}"
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

def load_project(project):
    global PROJ, BASE, CLIPS, NARR, RENDER, FPS, TOTAL
    PROJ = project
    BASE = f"/home/z/my-project/engine/projects/{PROJ}"
    CLIPS = f"{BASE}/clips"; NARR = f"{BASE}/narration"; RENDER = f"{BASE}/render"
    cfg_p = f"{BASE}/config.json"
    cfg = json.load(open(cfg_p)) if os.path.exists(cfg_p) else {}
    FPS = int(cfg.get("fps", 30)); TOTAL = float(cfg.get("total", 2040.0))

def syspath():
    sys.path.insert(0, f"/home/z/my-project/engine/pipeline")
    if os.path.exists(f"{BASE}/script_beats.py"):
        sys.path.insert(0, BASE)
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
    if len(pool) < 3:  # global fallback: primary subject footage
        primary = json.load(open(f"{BASE}/config.json")).get("primary_tag", "blackpink")
        for v, meta in sources.items():
            if primary in meta["subject_tags"]:
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
    frames[-1] += FPS * round(TOTAL) - sum(frames)   # exact frame count
    for t, f in zip(tl, frames):
        t["frames"] = f; t["dur"] = round(f / FPS, 6)
    off = 0.0
    for t in tl:
        t["start"] = round(off, 4); t["voice_at"] = round(off + 0.8, 4)
        off += t["dur"]
    tl[-1]["end"] = TOTAL
    json.dump(tl, open(f"{RENDER}/timeline.json", "w"), indent=1)
    build_cues(tl)
    build_caption_master(tl)
    print(f"plan: {len(tl)} beats, sum={sum(t['dur'] for t in tl):.3f}s, "
          f"clips assigned={sum(len(t['clips']) for t in tl)}")

def build_cues(tl):
    """One score cue per act (preset from config.acts), boundaries at beat starts."""
    cfgp = f"{BASE}/config.json"
    cfg = json.load(open(cfgp)) if os.path.exists(cfgp) else {}
    acts = {a["act"]: a for a in cfg.get("acts", [])}
    groups = {}
    # derive act numbers from beat ids: co* -> act 0, a<k>* -> act k
    import re
    for t in tl:
        m = re.match(r"a(\d+)", t["id"])
        act = int(m.group(1)) if m else 0
        groups.setdefault(act, []).append(t)
    cues = []
    for act, ts in sorted(groups.items()):
        t0 = min(t["start"] for t in ts); t1 = max(t["start"] + t["dur"] for t in ts)
        a = acts.get(act, {})
        cues.append({"t0": round(t0, 2), "t1": round(t1, 2),
                     "preset": a.get("preset", "overture"),
                     "intensity": a.get("intensity", 0.5),
                     "root": a.get("root", "D3"), "minor": a.get("minor", True)})
    # extend last cue to TOTAL (score covers the whole film)
    if cues:
        cues[-1]["t1"] = TOTAL
        cues[0]["t0"] = 0.0
    json.dump({"total": TOTAL, "cues": cues}, open(f"{RENDER}/cues.json", "w"), indent=1)
    print(f"cues: {len(cues)} from acts {sorted(groups)}")

# ---------------- captions (word-timed ASS) ----------------
ASS_HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Noto Serif SC,44,&H00EAF2F5,&H00FFFFFF,&H00140D06,&H90000000,0,0,0,0,100,100,0,0,1,2.4,1.2,2,230,230,56,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def _ass_time(t):
    if t < 0: t = 0
    cs = int(round(t * 100)); return f"{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}"

def _ass_esc(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")").strip()

def beat_caption_events(bid, base):
    """Word-timed events for one beat. base = film-time of beat t=0.
    Returns [(start, end, text)] in film time."""
    wp = f"{NARR}/{bid}.words.json"
    if not os.path.exists(wp): return []
    words = json.load(open(wp))
    if not words: return []
    # 1) words -> lines (<=38 chars, break on 0.55s gaps)
    lines = []
    for w in words:
        t0 = base + w["t"]; t1 = t0 + max(w["d"], 0.18)
        txt = w["w"].strip()
        if not txt: continue
        if lines and t0 - lines[-1][1] < 0.55 and len(lines[-1][2] + " " + txt) <= 38:
            lines[-1][1] = t1; lines[-1][2] += " " + txt
        else:
            lines.append([t0, t1, txt])
    # 2) lines -> events (max 2 lines, gap<0.7, dur<=6.0)
    evs = []
    for ln in lines:
        if evs and len(evs[-1][2]) < 2 and ln[0] - evs[-1][1] < 0.7 \
           and (evs[-1][1] - evs[-1][0]) <= 6.0:
            evs[-1][1] = ln[1]; evs[-1][2].append(_ass_esc(ln[2]))
        else:
            evs.append([ln[0], ln[1], [_ass_esc(ln[2])]])
    return [(round(e[0], 2), round(e[1] + 0.12, 2), "\\N".join(e[2])) for e in evs]

def build_caption_master(tl):
    evs = []
    for t in tl:
        if t["voice"] > 0:
            evs += beat_caption_events(t["id"], t["voice_at"])
    evs.sort()
    with open(f"{RENDER}/captions.ass", "w") as f:
        f.write(ASS_HDR)
        for s, e, txt in evs:
            f.write(f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Cap,,0,0,0,,{txt}\n")
    json.dump(evs, open(f"{RENDER}/caption_events.json", "w"))
    print(f"captions: {len(evs)} events")

def segment_ass(t, d):
    """Write segment-local ASS for beat; returns path or None.
    Voice starts 0.8s into the segment, so beat-local caption time = 0.8 + word.t."""
    evs = []
    if t["voice"] > 0:
        evs = beat_caption_events(t["id"], 0.8)   # beat-local: voice_at offset = 0.8s
    local = []
    for gs, ge, txt in evs:
        ls, le = gs, ge
        if le <= 0.05 or ls >= d - 0.05: continue
        local.append((max(0.05, ls), min(d - 0.05, le), txt))
    if not local: return None
    p = f"{RENDER}/ass/{t['id']}.ass"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(ASS_HDR)
        for s, e, txt in local:
            f.write(f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Cap,,0,0,0,,{txt}\n")
    return p

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

def _sub_filter(assp):
    a = assp.replace(":", r"\:").replace("'", r"\'")
    return f"subtitles=filename='{a}'"

def stage_segments():
    tl = json.load(open(f"{RENDER}/timeline.json"))
    os.makedirs(RENDER, exist_ok=True)
    os.makedirs(f"{RENDER}/ass", exist_ok=True)
    fallback = None
    for f in sorted(os.listdir(CLIPS)):
        if f.startswith("seg_") and f.endswith(".mp4"):
            fallback = f"{CLIPS}/{f}"; break
    for i, t in enumerate(tl):
        out = f"{RENDER}/seg_{t['id']}.mp4"
        if os.path.exists(out) and abs(_dur(out) - t["dur"]) < 0.05:
            continue
        d = t["dur"]
        assp = segment_ass(t, d)
        sub = ("," + _sub_filter(assp)) if assp else ""
        if t["kind"] == "card" and t["clips"]:
            src = t["clips"][0] if os.path.exists(t["clips"][0]) else fallback
            if src is None: continue
            cf, last = card_filter(t)
            if assp:
                cf += f";[{last}]{_sub_filter(assp)}[vsub]"; last = "vsub"
            cmd = ["ffmpeg","-y","-nostdin","-stream_loop","-1","-i",src,
                   "-filter_complex",cf,"-map",f"[{last}]","-t",f"{d:.4f}"] + ENC + [out]
        elif t["kind"] == "card":
            cf, last = card_filter(t)
            if assp:
                cf += f";[{last}]{_sub_filter(assp)}[vsub]"; last = "vsub"
            cmd = ["ffmpeg","-y","-nostdin","-f","lavfi","-i",
                   f"color=c=0x0a0a0a:s=1920x1080:r={FPS}:d={d:.4f}",
                   "-filter_complex",cf,"-map",f"[{last}]","-t",f"{d:.4f}"] + ENC + [out]
        else:
            picks = [c for c in t["clips"] if os.path.exists(c)] or ([fallback] if fallback else [])
            if not picks: continue
            n = len(picks); per = d / n
            cmd = ["ffmpeg","-y","-nostdin"]
            for c in picks: cmd += ["-stream_loop","-1","-i",c]
            fc = [f"[{j}:v]scale=1920:1080:flags=lanczos,fps={FPS},setsar=1,"
                  f"format=yuv420p,trim=duration={per:.4f},setpts=PTS-STARTPTS[c{j}]"
                  for j in range(n)]
            chain = "".join(f"[c{j}]" for j in range(n)) + f"concat=n={n}:v=1:a=0"
            if i == 0: chain += ",fade=t=in:st=0:d=1.2"
            if t["id"] == tl[-1]["id"]: chain += f",fade=t=out:st={max(0.1,d-2.0)}:d=2.0"
            chain += sub
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

# ---------------- audio v2 ----------------
SR = 48000

def stage_audio():
    tl = json.load(open(f"{RENDER}/timeline.json"))
    os.makedirs(f"{RENDER}/wav", exist_ok=True)
    from scipy.signal import butter, sosfilt
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    sys.path.insert(0, "/home/z/my-project/engine/pipeline/music")
    from sfx import limit
    import numpy as np
    N = int(round(TOTAL * SR))
    hp = butter(2, 85, "high", fs=SR, output="sos")
    # 1) narration -> normalized mono voice track
    voice = np.zeros(N, dtype=np.float32)
    for t in tl:
        if t["voice"] <= 0: continue
        src = f"{NARR}/{t['id']}.mp3"; dst = f"{RENDER}/wav/{t['id']}.wav"
        if not os.path.exists(dst):
            sh(["ffmpeg","-y","-nostdin","-i",src,"-ar",str(SR),"-ac","1",
                "-c:a","pcm_s16le",dst])
        with wave.open(dst) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        x = data.astype(np.float32) / 32768.0
        x = sosfilt(hp, x).astype(np.float32)
        pk = float(np.abs(x).max())
        if pk > 0: x *= 0.82 / pk
        start = int(t["voice_at"] * SR)
        end = min(N, start + len(x))
        voice[start:end] += x[:end - start]
    print("voice track placed", flush=True)
    # 2) duck envelope (opuscar convention: dilate 160ms, smooth 250ms, -9 dB)
    vad = (np.abs(voice) > 0.02).astype(np.float32)
    vad = maximum_filter1d(vad, size=int(0.16 * SR))
    duck = 1.0 - 0.65 * uniform_filter1d(vad, size=int(0.25 * SR))
    del vad
    duck = duck.astype(np.float32)
    # 3) stream bed + sum + chunked limiter -> mix.wav (true stereo)
    import soundfile as sf
    bedf = sf.SoundFile(f"{RENDER}/bed.wav")
    assert int(bedf.samplerate) == SR, bedf.samplerate
    OVL = SR  # 1s limiter context
    with wave.open(f"{RENDER}/mix.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        CH = SR * 30
        s0 = 0
        while s0 < N:
            e0 = min(N, s0 + CH)
            bed = np.zeros((e0 - s0 + 2 * OVL, 2), np.float32)
            bs = max(0, s0 - OVL)
            bedf.seek(bs)
            raw = bedf.read(min(len(bed), int(bedf.frames) - bs), dtype="float32", always_2d=True)
            bed[:len(raw)] = raw
            vo = np.zeros(len(bed), np.float32)
            vs, ve = max(0, s0 - OVL), min(N, e0 + OVL)
            vo[:ve - vs] = voice[vs:ve]
            dk = np.zeros(len(bed), np.float32)
            dk[:ve - vs] = duck[vs:ve]
            mix = vo[:, None] * 0.92 + bed * (dk * 0.5)[:, None]
            for c in range(2):
                mix[:, c] = limit(mix[:, c].astype(np.float64), .97).astype(np.float32)
            o0 = s0 - bs
            chunk = mix[o0:o0 + (e0 - s0)]
            stereo = np.empty((len(chunk), 2), dtype=np.int16)
            stereo[:, 0] = np.clip(chunk[:, 0] * 32767.0, -32767, 32767).astype(np.int16)
            stereo[:, 1] = np.clip(chunk[:, 1] * 32767.0, -32767, 32767).astype(np.int16)
            w.writeframes(stereo.tobytes())
            s0 = e0
            print(f"mix {s0/SR:.0f}/{TOTAL:.0f}s", flush=True)
    print(f"audio: mix.wav {N/SR:.1f}s written (true stereo)")

def stage_final():
    tl = json.load(open(f"{RENDER}/timeline.json"))
    with open(f"{RENDER}/concat.txt", "w") as f:
        for t in tl: f.write(f"file '{RENDER}/seg_{t['id']}.mp4'\n")
    # single-pass: concat + audio + LINEAR loudnorm (no pumping) -> final.mp4
    ln_p = f"{RENDER}/loudnorm.json"
    if not os.path.exists(ln_p):
        r = subprocess.run(["ffmpeg","-nostdin","-i",f"{RENDER}/mix.wav",
            "-af","loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json","-f","null","-"],
            capture_output=True, text=True)
        import re as _re
        m = _re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, _re.S)
        if not m: raise RuntimeError("loudnorm measure failed: " + r.stderr[-400:])
        meas = json.loads(m.group(0))
        json.dump(meas, open(ln_p, "w"))
    meas = json.load(open(ln_p))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true"
          f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
          f":measured_LRA={meas['input_lra']}:measured_thresh={meas["input_thresh"]}")
    sh(["ffmpeg","-y","-nostdin","-f","concat","-safe","0","-i",f"{RENDER}/concat.txt",
        "-i",f"{RENDER}/mix.wav",
        "-filter_complex",f"[1:a]{af}[outa]",
        "-map","0:v","-map","[outa]","-c:v","copy",
        "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
        "-movflags","+faststart",f"{BASE}/final.mp4"])
    p = subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_name,width,height,sample_rate,channels",
        "-of","json",f"{BASE}/final.mp4"], capture_output=True, text=True)
    print("QC:", p.stdout)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) >= 2: load_project(args[1])
    else: load_project(PROJ)
    os.makedirs(RENDER, exist_ok=True)
    {"plan": stage_plan, "segments": stage_segments,
     "audio": stage_audio, "final": stage_final}[args[0]]()
