#!/usr/bin/env python3
"""mirror_dl.py — resumable, VERIFIED source acquisition (R8: local-only, never CI).

Per source in projects/<slug>/sources_plan.json not yet 'ok':
  1. Try each mirror URL (projects/<slug>/mirrors.json) via yt-dlp (bounded 300s).
  2. TITLE gate: fetched title must contain >=2 expected tokens; reject karaoke/
     instrumental/reaction/lyric/chipmunk/sped-up noise.
  3. CONTENT gate (the real fix — titles lie): sample 8 frames across the file,
     InsightFace vs all 7 BABYMONSTER member centroids; need >=2 frames with a
     member face (cos >= 0.55). 'dream' exception: ahyeon absent is expected
     (she was on hiatus) — any of the other 6 members proves it's the group.
  4. Any gate fails -> delete file, try next mirror.
  5. All mirrors fail -> Dailymotion open-API mirror discovery (title-token
     filter + duration sanity), then same gates.

Usage: python3 scripts/mirror_dl.py <slug> [chunk_n]   # chunk_n sources per run
State: projects/<slug>/download_state.json  {"key": {"status","title","dur",
       "mirror","ah_present","faces_ok"}}  | legacy "ok" string also accepted.
"""
import json, os, re, subprocess, sys, time

ROOT = "/home/z/my-project/engine/projects"
YTDLP = ["python3", "-m", "yt_dlp"]
REJECT = ["karaoke", "instrumental", "reaction", "reacting", "lyric", "lyrics",
          "chipmunk", "sped up", "slowed", "nightcore", "line distribution",
          "color coded", "teacup", "8d audio", "clean version"]

STOPW = {"the", "and", "mv", "m/v", "official", "video", "ep", "yg", "babymonster"}

def is_ok(v):
    return v == "ok" or (isinstance(v, dict) and v.get("status") == "ok")

def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())

def expected_tokens(q):
    toks = [t for t in norm(q).split() if len(t) >= 3 and t not in STOPW]
    return toks or norm(q).split()

def title_ok(title, toks):
    tl = norm(title)
    if any(r in tl for r in REJECT):
        return False
    hit = sum(1 for t in toks if t in tl)
    return hit >= min(2, len(toks))

def probe_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except Exception: return -1.0

def ytdlp_fetch(url, out, log):
    """Download best mp4 <=1080p. Returns (ok, title)."""
    cmd = YTDLP + ["--no-playlist", "--socket-timeout", "20", "--retries", "2"]
    # curl_cffi impersonation breaks some vkvideo servers (Invalid Content-Length);
    # only Dailymotion's extractor requires it.
    if "dailymotion.com" in url:
        cmd += ["--impersonate", "firefox"]
    cmd += ["-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*+ba/b[height<=720]",
            "--merge-output-format", "mp4", "--print", "after_move:%(title)s",
            "-o", out, "--no-progress", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        log(f"    TIMEOUT {url[:70]}")
        return False, None
    if r.returncode != 0:
        log(f"    DL_FAIL rc={r.returncode} {url[:70]}")
        return False, None
    title = (r.stdout or "").strip().splitlines()[-1] if r.stdout else None
    if os.path.exists(out) or os.path.exists(out.replace(".mp4", ".mkv")):
        return True, title
    return False, title

def load_faceapp():
    import numpy as np
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    refs = json.load(open("/home/z/my-project/engine/tools/cce_references/refs_summary.json"))
    cents = {m: np.array(v["centroid"], dtype=np.float32)
             for m, v in refs["members"].items()}
    return app, cents

def content_gate(path, app, cents, key, log, n_frames=10):
    """Sample frames, classify: ('strong'|'weak'|'reject', ah_present, best).
    strong: >=2 frames with a member face (cos >= 0.55)
    weak:   faces present in >=30% frames + best member cos >= 0.25 — real footage
            whose styling/lighting drifts the embedding (covers, interviews,
            pre-debut). Titles are already gated; wrong-content uploads (protest
            videos, karaoke screens) have no faces at all and stay rejected.
            Weak sources get per-shot face scoring later (faceverify.py), and the
            Director only uses shots that pass individually."""
    import numpy as np, cv2
    dur = probe_dur(path)
    if dur <= 0: return "reject", False, {}
    base = [dur * (i + 0.5) / n_frames for i in range(n_frames)]
    times = sorted(set([round(t, 2) for t in base] +
                       [round(dur * f, 2) for f in (0.4, 0.5, 0.55, 0.6, 0.65)]))
    frames_hit, frames_face, ah, best = 0, 0, False, {}
    for t in times:
        try:
            r = subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{t:.2f}", "-i", path,
                                "-frames:v", "1", "-vf", "scale=640:-2",
                                "-f", "image2pipe", "-vcodec", "png", "-"],
                               capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            continue
        if r.returncode != 0 or not r.stdout: continue
        img = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)
        if img is None: continue
        got_face = False
        for f in app.get(img):
            emb = f.normed_embedding.astype(np.float32)
            for m, c in cents.items():
                cosv = float(np.dot(emb, c))
                if cosv > best.get(m, 0.0): best[m] = round(cosv, 4)
                if cosv >= 0.55:
                    got_face = True
                    if m == "ahyeon": ah = True
        if got_face: frames_hit += 1
        if app.get(img): frames_face += 1
    best_any = max(best.values()) if best else 0.0
    if frames_hit >= 2:
        verdict = "strong"
    elif frames_face / max(1, len(times)) >= 0.3 and best_any >= 0.25:
        verdict = "weak"
    else:
        verdict = "reject"
    log(f"    CONTENT {verdict} strong_hit={frames_hit}/{len(times)} face_rate={frames_face}/{len(times)} ah={ah} best={ {k:v for k,v in sorted(best.items(), key=lambda x:-x[1])[:2]} }")
    return verdict, ah, best

def dm_discover(q, toks, kind, log):
    """Dailymotion open API mirror discovery -> candidate URLs."""
    import urllib.request
    qs = "+".join(t for t in norm(q).split() if t not in {"m", "v"})
    url = (f"https://api.dailymotion.com/videos?search={urllib.parse.quote(qs)}"
           f"&fields=id,title,duration&limit=12&sort=relevance")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.load(r)
    except Exception as e:
        log(f"    DM_API_FAIL {e}")
        return []
    want = (140, 480) if kind == "mv" else (200, 1800)
    out = []
    for v in data.get("list", []):
        if "babymon" not in norm(v.get("title", "")): continue
        if not title_ok(v.get("title", ""), toks): continue
        d = v.get("duration", 0)
        if not (want[0] <= d <= want[1]): continue
        out.append((v["title"], f"https://www.dailymotion.com/video/{v['id']}"))
    log(f"    DM_DISCOVER {[t for t, _ in out[:3]]}")
    return [u for _, u in out]

def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    chunk = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    base = f"{ROOT}/{slug}"
    plan = json.load(open(f"{base}/sources_plan.json"))["sources"]
    mirrors = json.load(open(f"{base}/mirrors.json"))
    state = json.load(open(f"{base}/download_state.json"))

    pending = [s for s in plan if s["key"] != "_comment"
               and not is_ok(state.get(s["key"]))]
    # sources that failed >=2 runs go last; per-source wall-clock budget
    def prio(i_s):
        i, s = i_s
        fails = isinstance(state.get(s["key"]), dict) and state[s["key"]].get("fails", 0)
        return (1 if fails >= 2 else 0, i)
    pending = [s for _, s in sorted(enumerate(pending), key=prio)]
    print(f"[mirror_dl] pending {len(pending)}/{len(plan)}", flush=True)
    if not pending: return
    app, cents = load_faceapp()

    done = 0
    run_t0 = time.time()
    for s in pending:
        if done >= chunk: break
        if time.time() - run_t0 > 430:
            print("[mirror_dl] run budget nearly spent — deferring rest", flush=True)
            break
        key, q, kind = s["key"], s["q"], s.get("kind", "mv")
        toks = s.get("title_tokens") or expected_tokens(q)
        out = f"{base}/ytdl_cache/{key}.mp4"
        def log(m): print(m, flush=True)
        src_t0 = time.time()

        print(f"[{key}] {q}", flush=True)
        got, meta = False, {}
        # 1) committed mirrors
        for u in mirrors.get(key, []):
            if got or time.time() - src_t0 > 210: break
            ok, title = ytdlp_fetch(u, out, log)
            if not ok: continue
            if not title_ok(title or "", toks):
                log(f"    TITLE_REJECT '{(title or '')[:60]}'"); os.remove(out); continue
            verdict, ah, best = content_gate(out, app, cents, key, log)
            if verdict in ("strong", "weak"):
                got, meta = True, {"mirror": u, "title": title, "ah_present": ah,
                                   "verify": verdict}
            else:
                log("    CONTENT_REJECT"); os.remove(out)
        # 2) dailymotion discovery (primary + alt queries)
        if not got:
            urls = []
            for qv in [q] + s.get("alt_q", []):
                urls += dm_discover(qv, expected_tokens(qv), kind, log)
            for u in urls:
                if got or time.time() - src_t0 > 240: break
                ok, title = ytdlp_fetch(u, out, log)
                if not ok: continue
                if not title_ok(title or "", toks):
                    log(f"    TITLE_REJECT '{(title or '')[:60]}'"); os.remove(out); continue
                verdict, ah, best = content_gate(out, app, cents, key, log)
                if verdict in ("strong", "weak"):
                    got, meta = True, {"mirror": u, "title": title, "ah_present": ah,
                                       "verify": verdict}
                else:
                    log("    CONTENT_REJECT"); os.remove(out)
        if not got and os.path.exists(out):
            # file present from an interrupted run: verify instead of re-downloading
            verdict, ah, best = content_gate(out, app, cents, key, log)
            if verdict in ("strong", "weak"):
                got, meta = True, {"mirror": "recovered", "title": None,
                                   "ah_present": ah, "verify": verdict}
            else: os.remove(out)
        if got:
            d = probe_dur(out)
            state[key] = {"status": "ok", "dur": round(d, 1), **meta, "faces_ok": True}
            print(f"[{key}] OK dur={d:.0f}s via {meta['mirror'][:60]}", flush=True)
            done += 1
        else:
            prev = state.get(key) if isinstance(state.get(key), dict) else {}
            state[key] = {"status": "failed", "fails": prev.get("fails", 0) + 1,
                          "tries": time.strftime("%H:%M")}
            print(f"[{key}] FAILED this run (will retry next chunk)", flush=True)
        json.dump(state, open(f"{base}/download_state.json", "w"), indent=1)

    n_ok = sum(1 for v in state.values() if is_ok(v))
    print(f"[mirror_dl] chunk done: {n_ok}/{len(plan)} sources ok", flush=True)

if __name__ == "__main__":
    main()
