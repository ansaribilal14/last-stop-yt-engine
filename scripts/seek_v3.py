#!/usr/bin/env python3
"""seek_v3.py — v3.0 NEW-source acquisition (12 targets from user brief Appendix D).

Rebuilt after sandbox reset; incorporates ALL T13-SEEK diagnoses:
  - fmt string must not use arithmetic (width>=height*0.9 → SyntaxError) — aspect
    is enforced later by probe, not in the format filter.
  - yt-dlp native hlsnative hangs on vod3.cf.dmcdn.net → --downloader ffmpeg.
  - bilibili video pages are IP-blocked (412 + risk-control voucher) → bili is
    search-ONLY; downloads come from Dailymotion API discovery, committed direct
    URLs, and archive.org advancedsearch fallback.
  - Long files (sumersonic 1971s, taipei_4k ~2h) get per-target height caps,
    per-target ytdlp timeouts, and optional --download-sections windows so we
    only pull the Appendix-D timestamp ranges we actually need.

Gates per candidate: title tokens -> duration window -> face-content gate
(strong/weak, reused from mirror_dl) -> keep. Any fail: delete, next candidate.
State: projects/<slug>/download_state_v3.json (chunked, resumable).

Usage: python3 scripts/seek_v3.py [slug] [chunk_n]   # chunk_n targets per run
"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mirror_dl import content_gate, load_faceapp, probe_dur  # noqa: E402

ROOT = "/home/z/my-project/engine/projects"
YTDLP = ["python3", "-m", "yt_dlp"]
DEFAULT_FMT = "bv*[height<={h}][ext=mp4]+ba[ext=m4a]/b[height<={h}][ext=mp4]/bv*+ba/b[height<=480]"

# --- 12 v3.0 targets (brief Appendix D1/D2/D3) --------------------------------
TARGETS = [
    dict(key="apt_incheon", kind="stage", dur=(15, 900), h=720, t=300,
         q="BabyMonster Ahyeon airport Incheon",
         alts=["Ahyeon airport solo crowd", "Ahyeon Incheon airport 2024", "아현 공항 직캠"]),
    dict(key="gmp_ot7", kind="stage", dur=(15, 900), h=720, t=300,
         q="BABYMONSTER airport Gimpo fans",
         alts=["BABYMONSTER OT7 airport", "Babymonster airport chaos 2024"]),
    dict(key="hnd_2026", kind="stage", dur=(15, 900), h=720, t=300,
         q="Ahyeon airport Haneda Japan",
         alts=["BABYMONSTER airport Japan 2026", "Ahyeon airport walk 2026"]),
    dict(key="icn_2026", kind="stage", dur=(15, 900), h=720, t=300,
         q="Ahyeon airport September 2026",
         alts=["Ahyeon Incheon 2026 fans", "BabyMonster airport 2026 fancam"]),
    dict(key="gmp_short", kind="stage", dur=(15, 900), h=720, t=300,
         q="Ahyeon airport short hair 2025",
         alts=["Ahyeon 250313 airport", "Ahyeon Gimpo 2025"]),
    dict(key="taipei_4k", kind="stage", dur=(240, 5400), h=720, t=560,
         sections=["56:30-59:30", "59:45-61:45", "78:45-80:45"],
         q="BABYMONSTER LOVE MONSTERS Taipei",
         alts=["BABYMONSTER fan concert Taipei full", "LOVE MONSTERS ASIA FAN CONCERT"]),
    dict(key="taipei_moment", kind="stage", dur=(15, 300), h=720, t=300,
         q="Ahyeon Taipei cute stage moment",
         alts=["Ahyeon falls stage Taipei HOT SAUCE", "Ahyeon LOVE MONSTER fans smiling"]),
    dict(key="kyocera_hype", kind="stage", dur=(15, 900), h=720, t=300,
         q="BabyMonster Kyocera Dome crowd",
         alts=["Ahyeon hyping crowd sing along", "BABYMONSTER Blackpink Kyocera Dome"]),
    dict(key="soundcheck", kind="stage", dur=(15, 900), h=720, t=300,
         q="BABYMONSTER soundcheck fancam",
         alts=["Ahyeon soundcheck Hello Monsters", "BABYMONSTER Hello Monsters soundcheck"]),
    dict(key="sheesh_facecam", kind="stage", dur=(170, 300), h=720, t=300,
         q="AHYEON SHEESH facecam Inkigayo",
         alts=["베이비몬스터 아현 직캠 SHEESH", "Ahyeon SHEESH fancam 4K"]),
    dict(key="drip_facecam", kind="stage", dur=(170, 300), h=720, t=300,
         q="AHYEON DRIP facecam Inkigayo",
         alts=["아현 직캠 DRIP", "Ahyeon DRIP fancam 4K"]),
    dict(key="sumersonic", kind="stage", dur=(1500, 2400), h=480, t=560,
         direct=["https://www.dailymotion.com/video/x9b5d1a"],
         q="BabyMonster Summer Sonic 2025",
         alts=["Really Like You Live Summer Sonic Osaka", "BABYMONSTER Summer Sonic"]),
]

# token gate: candidate title must mention the act, not a karaoke/reupload channel
REJECT = ["karaoke", "instrumental", "reaction", "reacting", "lyric", "lyrics",
          "chipmunk", "sped up", "slowed", "nightcore", "line distribution",
          "color coded", "8d audio", "dance practice mirror", "tutorial"]
NEED_ANY = ["babymon", "ahyeon", "아현", "베이비몬스터", "ahyeon"]


def log(m): print(m, flush=True)


def title_gate(title, target):
    tl = title.lower()
    if any(r in tl for r in REJECT): return False
    return any(n in tl for n in NEED_ANY)


def dm_search(qs, dmin, dmax, limit=25):
    """Dailymotion open API -> [(title, url, dur)]."""
    out = []
    for q in qs:
        url = ("https://api.dailymotion.com/videos?search=" + urllib.parse.quote(q)
               + "&fields=id,title,duration&limit=%d&sort=relevance" % limit)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.load(r)
        except Exception as e:
            log(f"    DM_API_FAIL {q[:40]}: {e}"); continue
        for v in data.get("list", []):
            d = v.get("duration", 0)
            if not (dmin <= d <= dmax): continue
            if not title_gate(v.get("title", ""), q): continue
            out.append((v["title"], f"https://www.dailymotion.com/video/{v['id']}", d))
    seen, uniq = set(), []
    for t, u, d in out:
        if u not in seen: seen.add(u); uniq.append((t, u, d))
    return uniq


def ia_search(qs, dmin, dmax):
    """archive.org advancedsearch fallback -> [(title, url, dur)]."""
    out = []
    for q in qs[:2]:
        url = ("https://archive.org/advancedsearch.php?q=" + urllib.parse.quote(q)
               + "&fl%5B%5D=identifier&fl%5B%5D=title&rows=8&output=json")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.load(r)
        except Exception:
            continue
        for doc in data.get("response", {}).get("docs", []):
            t = doc.get("title", "")
            if not title_gate(t, q): continue
            out.append((t, f"https://archive.org/details/{doc['identifier']}", -1))
    return out


def ytdlp_fetch(url, out, height, timeout, sections=None):
    """Download with T13-fixed fmt + ffmpeg downloader. Returns (ok, title)."""
    cmd = YTDLP + ["--no-playlist", "--socket-timeout", "20", "--retries", "2"]
    if "dailymotion.com" in url:
        cmd += ["--impersonate", "firefox"]
    cmd += ["--downloader", "ffmpeg"]
    if sections:
        for s in sections:
            cmd += ["--download-sections", f"*{s}"]
        cmd += ["--force-keyframes-at-cuts"]
    cmd += ["-f", DEFAULT_FMT.format(h=height),
            "--merge-output-format", "mp4", "--print", "after_move:%(title)s",
            "-o", out, "--no-progress", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"    TIMEOUT {url[:70]}")
        return False, None
    if r.returncode != 0:
        tail = (r.stderr or "")[-200:].replace("\n", " ")
        log(f"    DL_FAIL rc={r.returncode} {url[:70]} …{tail[-120:]}")
        return False, None
    title = (r.stdout or "").strip().splitlines()[-1] if r.stdout else None
    if os.path.exists(out) or os.path.exists(out.replace(".mp4", ".mkv")):
        return True, title
    return False, title


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    chunk = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    base = f"{ROOT}/{slug}"
    os.makedirs(f"{base}/ytdl_cache", exist_ok=True)
    spath = f"{base}/download_state_v3.json"
    state = json.load(open(spath)) if os.path.exists(spath) else {}

    pending = [t for t in TARGETS if (state.get(t["key"]) or {}).get("status") != "ok"]
    pending.sort(key=lambda t: (state.get(t["key"], {}).get("fails", 0) >= 2, 0))
    log(f"[seek_v3] pending {len(pending)}/{len(TARGETS)}")
    if not pending:
        return
    app, cents = load_faceapp()

    done, run_t0 = 0, time.time()
    for t in pending:
        if done >= chunk or time.time() - run_t0 > 430:
            log("[seek_v3] run budget spent — deferring rest"); break
        key, out = t["key"], f"{base}/ytdl_cache/{t['key']}.mp4"
        log(f"[{key}] {t['q']}")
        t0 = time.time()
        cands = [(ti, u, d) for ti, u, d in dm_search([t["q"]] + t.get("alts", []),
                                                      t["dur"][0], t["dur"][1])]
        log(f"    DM cands: {len(cands)}")
        got, meta = False, {}
        # 1) committed direct URLs first (known-good mirrors)
        for u in t.get("direct", []):
            if got or time.time() - t0 > t["t"] // 2: break
            ok, title = ytdlp_fetch(u, out, t["h"], t["t"], t.get("sections"))
            if ok:
                verdict, ah, best = content_gate(out, app, cents, key, log)
                if verdict in ("strong", "weak"):
                    got, meta = True, {"mirror": u, "verify": verdict, "ah": ah}
                else:
                    log("    CONTENT_REJECT (direct)"); os.remove(out)
        # 2) discovered candidates
        for ti, u, d in cands:
            if got or time.time() - t0 > t["t"]: break
            if not title_gate(ti, t["q"]): continue
            ok, _ = ytdlp_fetch(u, out, t["h"], min(300, t["t"]), t.get("sections"))
            if not ok: continue
            verdict, ah, best = content_gate(out, app, cents, key, log)
            if verdict in ("strong", "weak"):
                got, meta = True, {"mirror": u, "title": ti, "verify": verdict, "ah": ah}
            else:
                log(f"    CONTENT_REJECT '{ti[:50]}'"); os.remove(out)
        # 3) archive.org fallback (low probability, cheap)
        if not got:
            for ti, u, _ in ia_search([t["q"]] + t.get("alts", []), *t["dur"]):
                if got: break
                ok, _ = ytdlp_fetch(u, out, t["h"], 240, t.get("sections"))
                if ok:
                    verdict, ah, best = content_gate(out, app, cents, key, log)
                    if verdict in ("strong", "weak"):
                        got, meta = True, {"mirror": u, "title": ti, "verify": verdict, "ah": ah}
                    else:
                        os.remove(out)
        if got:
            d = probe_dur(out)
            state[key] = {"status": "ok", "dur": round(d, 1), **meta}
            log(f"[{key}] OK dur={d:.0f}s via {meta['mirror'][:60]}")
            done += 1
        else:
            prev = state.get(key, {})
            state[key] = {"status": "failed", "fails": prev.get("fails", 0) + 1,
                          "tries": time.strftime("%H:%M")}
            log(f"[{key}] FAILED this run")
        json.dump(state, open(spath, "w"), indent=1)

    n_ok = sum(1 for t in TARGETS if (state.get(t["key"]) or {}).get("status") == "ok")
    log(f"[seek_v3] chunk done: {n_ok}/{len(TARGETS)} v3 targets ok")


if __name__ == "__main__":
    main()
