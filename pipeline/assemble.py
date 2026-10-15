#!/usr/bin/env python3
"""assemble.py v3 — EDITOR: executes the Director's EDL verbatim (T7).
Stages: plan | segments | audio | final
  python3 assemble.py <stage> [project]

v3 editorial contract (kills the playlist randomness):
  - plan:     reads scene_plan.json (Director-to-Editor contract) as the ONLY
              source of timing. Narration is the clock; lead/tail/slots come
              from the Director; frame-exact totals preserved. No pool shuffle,
              no duration redistribution, no clip lottery.
  - segments: renders each scene from its shot list — video shots trimmed at
              real source timecodes (2s preroll seek + frame-accurate trim),
              images animated with Ken Burns motion, cards over blurred bg
              loops, word-timed ASS captions burned per scene.
  - audio:    unchanged v2 path — narration placed at voice_at (authoritative
              word timings), opuscar-style ducking bed, two-pass loudnorm.
Spec: 1920x1080 30fps H.264 CRF16, AAC 192k 48kHz stereo, -14 LUFS.
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

# ---------------- v3 PLAN: Director EDL -> timeline ----------------
def stage_plan():
    """Convert scene_plan.json (Director) into render/timeline.json + cues +
    captions. The Director's lead/vd/tail structure is preserved EXACTLY:
    voice_at = scene.start + lead (word t=0 lands there), frames sum to TOTAL."""
    sp = None
    for cand in (f"{RENDER}/scene_plan.json", f"{BASE}/scene_plan.json"):
        if os.path.exists(cand):
            sp = json.load(open(cand)); break
    if sp is None:
        raise RuntimeError("scene_plan.json not found — run director.py first")
    tl = []
    for s in sp["scenes"]:
        tl.append({"id": s["beat"], "scene_id": s["id"], "kind": s["kind"],
                   "card": s.get("card"), "voice": s["narration"]["dur"],
                   "lead": s.get("lead", 0.8),
                   "slot": s["dur"], "frames": s["frames"],
                   "start": s["start"], "voice_at": s["voice_at"],
                   "shots": s.get("shots", []),
                   "music_cue": s.get("music_cue"), "dur": s["dur"]})
    total = sum(t["dur"] for t in tl)
    if abs(total - TOTAL) > 1.0:
        raise RuntimeError(f"scene_plan total {total:.2f}s != config TOTAL {TOTAL}s")
    json.dump(tl, open(f"{RENDER}/timeline.json", "w"), indent=1)
    build_cues(tl)
    build_caption_master(tl)
    n_shots = sum(len(t["shots"]) for t in tl)
    print(f"plan(v3): {len(tl)} scenes, {n_shots} EDL shots, sum={total:.3f}s "
          f"(frame-exact), voice_at preserved")

def build_cues(tl):
    """One score cue per act (preset from config.acts), boundaries at scene starts."""
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
    """Write scene-local ASS; voice starts at t['lead'], so caption time = lead + word.t."""
    evs = []
    lead = t.get("lead", 0.8)
    if t["voice"] > 0:
        evs = beat_caption_events(t["id"], lead)   # scene-local: voice_at offset = lead
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

def card_filter(t, bg_src):
    lines = t["card"].get("lines", []); ck = t["card"]["kind"]; d = t["dur"]
    bg_in = bool(bg_src) and os.path.exists(bg_src)
    fc = []
    if bg_in:
        fc.append(f"[0:v]fps={FPS},scale=1920:1080:flags=fast_bilinear,boxblur=24:2,"
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

# ---------------- v3 SEGMENTS: EDL executor ----------------
def _zb_filter(dur, motion, idx):
    """Ken Burns for one image shot -> labeled stream [k{idx}].
    zoompan at 1280x720 (2.25x cheaper than 1080p) then lanczos upscale —
    photographic context plates, visually indistinguishable."""
    frames = max(1, int(round(dur * FPS)))
    if motion == "pull_out":
        z = f"1.14-0.14*on/{frames}"
    else:  # push_in (default)
        z = f"1.0+0.14*on/{frames}"
    return (f"[{idx}:v]scale=1536:864:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1536:864,setsar=1,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s=1280x720:fps={FPS},scale=1920:1080:flags=lanczos,format=yuv420p,setsar=1,"
            f"trim=duration={dur:.4f},setpts=PTS-STARTPTS[k{idx}]")

def _vs_filter(shot, idx, want_dur, scene_local_start, file_dur=None):
    """Video shot from real source timecode -> labeled stream [v{idx}].
    2s preroll input seek + frame-accurate in-filter trim. EDL ranges are
    clamped to the real file duration. If the display window exceeds the
    EDL source range, source_in is pulled BACKWARD into the same source
    (real footage, editors' 'start a beat earlier') — tpad clone is kept
    only as a sub-second rounding guard because long clones render at
    ~0.15x realtime."""
    want = max(1.2, want_dur)
    sin = float(shot["source_in"]); sout = float(shot["source_out"])
    if file_dur and file_dur > 0:
        sout = min(sout, file_dur - 0.08)
    src_dur = max(0.5, sout - sin)
    if want > src_dur:
        sin = max(0.0, sin - (want - src_dur + 0.25))
        src_dur = max(0.5, sout - sin)
    use = min(want, src_dur)
    pre = 2.0 if sin >= 2.0 else sin
    seek = sin - pre
    trim0 = pre
    trim1 = pre + use
    pad = max(0.0, want - use + 0.15)
    return (f"[{idx}:v]trim=start={trim0:.3f}:end={trim1:.3f},setpts=PTS-STARTPTS,"
            f"scale=1920:1080:flags=lanczos,fps={FPS},setsar=1,format=yuv420p,"
            f"tpad=stop_mode=clone:stop_duration={pad:.3f},"
            f"trim=duration={want:.4f},setpts=PTS-STARTPTS[v{idx}]"), seek, use

def _kb_clip(p, dur, motion):
    """Animated context plate for one image, rendered ONCE and cached.
    zoompan is ~1s/frame at 720p (120s per clip) — replaced with:
      1. pre-scale the still once to 2112x1188
      2. loop it at 30fps, animate a 1920x1080 crop window across it
         (crop = pure slicing, no resample — near-zero cost)
    motion: push_in -> pan left-to-right, pull_out -> right-to-left,
            tilt -> downward tilt."""
    import hashlib
    h = hashlib.sha1(f"{p}|{dur:.3f}|{motion}".encode()).hexdigest()[:12]
    cdir = f"{RENDER}/kb_cache"
    os.makedirs(cdir, exist_ok=True)
    out = f"{cdir}/kb_{h}.mp4"
    if os.path.exists(out) and abs(_dur(out) - dur) < 0.06:
        return out
    tmp = out.replace(".mp4", ".tmp.mp4")
    scaled = f"{cdir}/s_{h}.png"
    if not os.path.exists(scaled):
        sh(["ffmpeg", "-y", "-nostdin", "-i", p,
            "-vf", "scale=2112:1188:force_original_aspect_ratio=increase:flags=lanczos,"
                    "crop=2112:1188", "-frames:v", "1", scaled])
    if motion == "pull_out":
        x = f"(iw-ow)*(1-t/{dur:.3f})"
    elif motion == "tilt":
        x = "(iw-ow)/2"
    else:  # push_in
        x = f"(iw-ow)*t/{dur:.3f}"
    y = f"(ih-oh)*t/{dur:.3f}" if motion == "tilt" else "(ih-oh)/2"
    fc = (f"[0:v]crop=1920:1080:x='{x}':y='{y}',setsar=1,format=yuv420p,"
          f"trim=duration={dur:.4f},setpts=PTS-STARTPTS[v]")
    sh(["ffmpeg", "-y", "-nostdin", "-loop", "1", "-framerate", str(FPS),
        "-t", f"{dur + 0.3:.3f}", "-i", scaled,
        "-filter_complex", fc, "-map", "[v]", "-an",
        "-t", f"{dur:.4f}"] + ENC + [tmp])
    os.replace(tmp, out)
    return out

def stage_segments():
    """Render each scene seg from its EDL shot list, verbatim."""
    tl = json.load(open(f"{RENDER}/timeline.json"))
    os.makedirs(RENDER, exist_ok=True)
    os.makedirs(f"{RENDER}/ass", exist_ok=True)
    failures = []
    for i, t in enumerate(tl):
        out = f"{RENDER}/seg_{t['id']}.mp4"
        tmp = out.replace(".mp4", ".tmp.mp4")
        if os.path.exists(out) and abs(_dur(out) - t["dur"]) < 0.05:
            continue
        d = t["dur"]
        lead = t.get("lead", 0.8)
        assp = segment_ass(t, d)
        sub = ("," + _sub_filter(assp)) if assp else ""
        shots = t.get("shots", [])

        if t["kind"] == "card":
            bg = next((s for s in shots if s.get("type") == "video"), None)
            bg_src = f"{BASE}/{bg['src']}" if bg else None
            cf, last = card_filter(t, bg_src)
            if assp:
                cf += f";[{last}]{_sub_filter(assp)}[vsub]"; last = "vsub"
            if bg_src:
                cmd = ["ffmpeg","-y","-nostdin","-stream_loop","-1","-i",bg_src,
                       "-filter_complex",cf,"-map",f"[{last}]","-an","-t",f"{d:.4f}"] + ENC + [tmp]
            else:
                cmd = ["ffmpeg","-y","-nostdin","-f","lavfi","-i",
                       f"color=c=0x0a0a0a:s=1920x1080:r={FPS}:d={d:.4f}",
                       "-filter_complex",cf,"-map",f"[{last}]","-an","-t",f"{d:.4f}"] + ENC + [tmp]
            sh(cmd); os.replace(tmp, out)
            print(f"[{i+1}/{len(tl)}] {t['id']} card {d:.1f}s ok", flush=True)
            continue

        # ---- clips / interlude: build the scene from ordered EDL shots ----
        inputs, fc, chains = [], [], []
        idx = 0
        _fdur_cache = {}
        def _fdur(p):
            if p not in _fdur_cache:
                _fdur_cache[p] = _dur(p)
            return _fdur_cache[p]
        # scene-local layout: shots span narration [lead, lead+vd]; extend first
        # shot left over the lead, last shot right over the tail (headroom-clamped)
        layout = []
        vd = float(t["voice"])
        for j, s in enumerate(shots):
            ds = lead + float(s.get("display_start", 0.0))
            de = lead + float(s.get("display_end", s.get("display_start", 0.0) + vd))
            layout.append([s, ds, de])
        if not layout:
            # no shots planned -> color fallback (recorded gap), still render scene
            cmd = ["ffmpeg","-y","-nostdin","-f","lavfi","-i",
                   f"color=c=0x101014:s=1920x1080:r={FPS}:d={d:.4f}",
                   "-vf", f"fade=t=in:st=0:d=1.0{sub}", "-an", "-t", f"{d:.4f}"] + ENC + [tmp]
            sh(cmd); os.replace(tmp, out)
            print(f"[{i+1}/{len(tl)}] {t['id']} EMPTY-fallback {d:.1f}s", flush=True)
            continue
        layout[0][1] = 0.0                    # first shot covers the lead
        layout[-1][2] = d                     # last shot covers the tail
        # video/image inputs
        openers = []
        for j, (s, ds, de) in enumerate(layout):
            dur_j = max(1.0, de - ds)
            if s["type"] == "image":
                p = f"{BASE}/{s['src']}"
                if not os.path.exists(p):
                    p = s["src"]
                # Ken Burns rendered once per (image,dur,motion), cached
                kbp = _kb_clip(p, dur_j, s.get("motion", "push_in"))
                inputs += ["-i", kbp]
                fc.append(f"[{idx}:v]fps={FPS},format=yuv420p,setsar=1,"
                          f"trim=duration={dur_j:.4f},setpts=PTS-STARTPTS[k{idx}]")
                chains.append(f"[k{idx}]")
                idx += 1
            else:
                src = s.get("src", "")
                src = src if os.path.isabs(src) else f"{BASE}/{src}"
                if not os.path.exists(src):
                    raise RuntimeError(f"scene {t['id']}: missing source {src}")
                vf, seek, use = _vs_filter(s, idx, dur_j, ds, file_dur=_fdur(src))
                inputs += ["-ss", f"{seek:.3f}", "-i", src]
                fc.append(vf)
                chains.append(f"[v{idx}]")
                idx += 1
        n = len(chains)
        concat = "".join(chains) + f"concat=n={n}:v=1:a=0"
        extra = ""
        if i == 0: extra += ",fade=t=in:st=0:d=1.2"
        if t["id"] == tl[-1]["id"] or t["id"].endswith("credits"): 
            extra += f",fade=t=out:st={max(0.1, d-2.0):.2f}:d=2.0"
        concat += extra + sub + "[vout]"
        fc.append(concat)
        cmd = (["ffmpeg","-y","-nostdin"] + inputs +
               ["-filter_complex", ";".join(fc), "-map", "[vout]", "-an",
                "-t", f"{d:.4f}"] + ENC + [tmp])
        try:
            sh(cmd)
            os.replace(tmp, out)
            print(f"[{i+1}/{len(tl)}] {t['id']} {n} shots {d:.1f}s ok", flush=True)
        except RuntimeError as e:
            print(f"[{i+1}/{len(tl)}] {t['id']} FAILED: {str(e)[-300:]}", flush=True)
            failures.append(t["id"])
            if os.path.exists(tmp): os.remove(tmp)
    if failures:
        print(f"SEGMENTS: {len(failures)} failed: {failures}", flush=True)
        raise RuntimeError(f"{len(failures)} scenes failed: {failures[:6]}")
    print("SEGMENTS: all scenes rendered", flush=True)

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
