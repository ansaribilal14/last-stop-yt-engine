#!/usr/bin/env python3
"""qa_ahyeon_claims.py — THE user-mandated check: when narration says 'Ahyeon',
the screen must show Ahyeon. Finds every spoken 'ahyeon' word via word timings,
extracts the film frame at that moment, runs InsightFace vs the character
centroid, reports per-claim scores. Human-review stills dumped for low scores.
"""
import json, os, subprocess, sys
import numpy as np, cv2

BASE_ROOT = "/home/z/my-project/engine/projects"
REFS = "/home/z/my-project/engine/tools/cce_references"


def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    base = f"{BASE_ROOT}/{proj}"
    final = f"{base}/final.mp4"
    tl = json.load(open(f"{base}/render/timeline.json"))
    summ = json.load(open(f"{REFS}/refs_summary.json"))
    cents = {m: np.array(v["centroid"], dtype=np.float32)
             for m, v in summ["members"].items()}
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"],
                       providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))

    # collect film-times where 'ahyeon' (or 'ah yeon') is spoken
    claims = []
    for i, t in enumerate(tl):
        if t["voice"] <= 0: continue
        off = sum(x["dur"] for x in tl[:i])
        wp = f"{base}/narration/{t['id']}.words.json"
        if not os.path.exists(wp): continue
        for w in json.load(open(wp)):
            txt = w.get("w", "").strip().lower().strip(".,!?—-\"'()")
            if txt in ("ahyeon", "ah-yeon", "ahyeon's", "ahyeon."):
                claims.append((t["id"], round(off + t.get("lead", 0.8) + w["t"] + w.get("d", 0.2) / 2, 2), w["w"]))
    print(f"spoken 'Ahyeon' mentions: {len(claims)}")

    rows = []
    os.makedirs(f"{base}/render/qa/claims", exist_ok=True)
    for k, (sid, ft, word) in enumerate(claims):
        r = subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{ft:.2f}", "-i", final,
                            "-frames:v", "1", "-vf", "scale=640:-2",
                            "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True, timeout=60)
        if r.returncode != 0 or not r.stdout:
            rows.append((sid, ft, "no-frame", 0.0)); continue
        img = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)
        best_ah, best_any, n_faces = 0.0, 0.0, 0
        for f in app.get(img):
            n_faces += 1
            emb = f.normed_embedding.astype(np.float32)
            for m, c in cents.items():
                s_ = float(np.dot(emb, c))
                best_any = max(best_any, s_)
                if m == "ahyeon": best_ah = max(best_ah, s_)
        verdict = ("AHYEOON" if best_ah >= 0.55 else
                   "likely" if best_ah >= 0.45 else
                   ("group/wide" if n_faces >= 2 or best_any >= 0.45 else
                    "no-face(logo/wide?)"))
        rows.append((sid, ft, f"{verdict}", round(best_ah, 2), n_faces))
        cv2.imwrite(f"{base}/render/qa/claims/{k:02d}_{sid}_{ft:.0f}s_ah{best_ah:.2f}.jpg", img)

    from collections import Counter
    vc = Counter(r[2] for r in rows)
    print("verdicts:", dict(vc))
    lows = [r for r in rows if r[2] in ("likely", "no-face(logo/wide?)")]
    print(f"\nweakest claims (review stills in render/qa/claims/):")
    for r in lows[:12]: print("  ", r)
    strong = sum(1 for r in rows if r[2] == "AHYEOON")
    print(f"\nSCORE: {strong}/{len(rows)} verified-Ahyeon closeups at mention; "
          f"{vc.get('group/wide',0)} group/wide; {vc.get('likely',0)} likely; "
          f"{vc.get('no-face(logo/wide?)',0)} no-face")

if __name__ == "__main__":
    main()
