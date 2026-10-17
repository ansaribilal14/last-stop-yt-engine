#!/usr/bin/env python3
"""director.py — THE DOCUMENTARY DIRECTOR (T4, permanent agent).

Invoked AFTER narration + word timings are finalized, BEFORE assembly.
Reads the story (beats, facts refs, narration words), the footage index
(shot boundaries + face scores), and the contextual image manifest — then
plans EVERY scene: what the audience sees at every moment, cut by cut,
matched to the spoken words. Emits scene_plan.json (the Editor executes it
verbatim) + EDIT_PLAN.md (the director's notes, human-readable).

Editorial doctrine (see docs/agents/DOCUMENTARY_DIRECTOR.md):
  - Narration is the clock. Shots derive from word timing, never from
    global duration redistribution.
  - Places get real imagery exactly when they are spoken.
  - Shots are cut on sentence/clause boundaries, mid-motion, at real shot
    boundaries of the sources — never arbitrary first-seconds.
  - Sequence grammar: establish -> develop -> emphasize; alternate sources;
    no repeated shot within 8 beats; Ahyeon presence verified per shot.
  - Missing asset -> recorded fallback, never a random substitute.

Deterministic: seed = project slug. Same inputs -> same plan.
Usage: python3 director.py <project>
"""
import json, math, os, random, re, sys

BASE_ROOT = "/home/z/my-project/engine/projects"

# ---------------- entity lexicon (word-level anchoring) ----------------
ENTITY_ALIASES = {
    "chuncheon": ["chuncheon"],
    "ygent": ["yg"],
    "gocheok": ["gocheok"],  # NOTE: bare "dome" is a metaphor trap ("dome-sized crowds")
    "seoul": ["seoul"],
    "gangwon": ["gangwon"],
    "practice_room": ["mirror", "mirrors", "practice"],
    "korea_context": ["korea", "korean"],
}
ENTITY_LABEL = {
    "chuncheon": "Chuncheon", "ygent": "YG Entertainment", "gocheok": "Gocheok Sky Dome",
    "seoul": "Seoul", "gangwon": "Gangwon Province", "practice_room": "practice room",
    "korea_context": "South Korea",
}
IMAGE_MIN_HOLD = 3.2     # shortest readable image (opuscar rule >= 1.8s; images need more)
IMAGE_MAX_HOLD = 5.0
LEAD = 0.8               # breath before narration inside each scene
TAIL_CLIPS = 4.5         # default air after narration in footage scenes
TAIL_MIN = 2.2
CARD_TARGET = {"title": 18.0, "chapter": 16.0, "stat": 12.0, "close": 20.0, "credits": 50.0}
INTERLUDE_DUR = 12.0
# R-v3: scene openers — the first video cut of these beats MUST come from the
# preferred source (fact-image alignment: s32 opens on the Incheon solo night
# the narration describes; s44 opens on the Taipei flower-cart moment).
OPENERS = {"a6b01": ["apt_incheon", "icn_2026"], "a8b02": ["taipei_moment"]}

def load_beats(proj):
    sys.path.insert(0, f"/home/z/my-project/engine/projects/{proj}")
    from script_beats import BEATS
    return BEATS

def words_for(base, bid):
    p = f"{base}/narration/{bid}.words.json"
    if not os.path.exists(p): return []
    return json.load(open(p))

def sentences(words, gap=0.55):
    """Split word stream into sentences: punctuation or >gap silence."""
    sents, cur = [], []
    for w in words:
        if not w.get("w", "").strip(): continue
        cur.append(w)
        t = w["w"].strip()
        if t.endswith((".", "!", "?")):
            sents.append(cur); cur = []
        elif cur and w["t"] - (cur[-2]["t"] + cur[-2].get("d", 0.2) if len(cur) > 1 else 0) > gap:
            sents.append(cur[:-1]); cur = [w]
    if cur: sents.append(cur)
    return [s for s in sents if s]

def clause_breaks(sent, gap=0.45):
    """Inside a long sentence, clause boundaries for multi-shot coverage."""
    if len(sent) < 12: return []
    brk = []
    for a, b in zip(sent, sent[1:]):
        if b["t"] - (a["t"] + a.get("d", 0.2)) > gap:
            brk.append(b["t"])
    return brk

def find_entity_hits(words):
    """word-level entity mentions: {entity: [word_time,...]} (beat-local seconds)."""
    hits = {}
    for w in words:
        txt = w.get("w", "").strip().lower().strip(".,!?—-\"'()")
        for ent, aliases in ENTITY_ALIASES.items():
            if any(a == txt or (a == "yg" and txt in ("yg", "y.g")) for a in aliases) \
               or any(a in txt and len(a) > 3 for a in aliases):
                hits.setdefault(ent, []).append(w["t"])
    return hits

def pick_image_asset(manifest, entity, state):
    """Rotate deterministically through verified assets; None if none.
    Rights gate: verified license/public-domain, and NEVER NoDerivatives
    (Ken Burns motion counts as a derivative)."""
    e = manifest.get("entities", {}).get(entity, {})
    assets = []
    for a in e.get("assets", []):
        lic = (a.get("provenance", {}).get("license_name", "") or "").upper()
        if a.get("rights_status") not in ("verified_license", "verified_public_domain"):
            continue
        if "ND" in lic.replace("NODERIVS", "ND").replace("NODERIVATIVE", "ND"):
            continue
        if not os.path.exists(a.get("file", {}).get("path", "")):
            continue
        assets.append(a)
    if not assets: return None
    k = state["img_cursor"].get(entity, 0)
    state["img_cursor"][entity] = k + 1
    return assets[k % len(assets)]

# ---------------- footage selection ----------------
def candidate_sources(beat, sources, primary):
    vids = list(beat.get("vids", []))
    if vids: return vids
    tagged = [v for v, m in sources.items()
              if any(t in m.get("subject_tags", []) for t in beat.get("tags", []))]
    if len(tagged) >= 2: return tagged
    return [v for v, m in sources.items() if primary in m.get("subject_tags", [])] or list(sources)

def section_for(intent):
    return {"calm": ("verse1", "verse2", "intro"), "build": ("verse2", "chorus1"),
            "peak": ("chorus2", "chorus1", "final_chorus"), "payoff": ("final_chorus", "chorus2")}.get(intent, ("chorus1",))

def score_shot(sh, want_dur, intent, recent_sources, used_shots, primary, rnd,
               subject_named=False):
    s = 0.0
    sec = section_for(intent)
    s += 2.2 if sh.get("section_hint") in sec else 0.0
    s += 2.4 * sh.get("ah_score", 0.0)                       # character edge
    if subject_named:
        # the sentence names Ahyeon: demand her on screen — verified presence
        # is rewarded hard, unverified group-wide shots are pushed down
        s += 2.6 if sh.get("ah_score", 0.0) >= 0.5 else 0.0
        if sh.get("ah_score", 0.0) < 0.35: s -= 1.6
        # R-v3 (issue #12): closeup preference — facecam sources are literal
        # closeups of her; reward them hard when she is named
        if "facecam" in (sh.get("src", "") or ""): s += 0.8
    dur_fit = 1.0 if sh["dur"] >= min(want_dur + 0.6, 8.0) else (sh["dur"] / max(0.5, want_dur))
    s += 1.2 * dur_fit
    target_motion = {"calm": 0.12, "build": 0.3, "peak": 0.55, "payoff": 0.45}.get(intent, 0.3)
    s += 0.9 * max(0.0, 1.0 - abs(sh.get("motion", 0.3) - target_motion))
    if sh.get("label") in recent_sources: s -= 1.1
    key = (sh.get("src"), sh["start"])
    if key in used_shots: s -= 4.0
    if sh.get("tags") and primary in sh["tags"]: s += 0.35
    s += rnd.random() * 0.4                                   # deterministic tie-break
    return s

def intent_curve(beat, sents, n_shots):
    """Map position in beat -> visual intent (calm/build/peak/payoff)."""
    act = beat.get("act", 1)
    cfg_i = {"overture": 0.55, "trainee": 0.42, "dawn": 0.5, "tension": 0.68,
             "triumph": 0.8, "warm": 0.75, "resolve": 0.6}
    return "peak" if act in (3, 5) and n_shots <= 2 else \
           ("build" if act in (2, 4) else "calm")

def plan_scene_shots(beat, vd, words, shots_index, sources, manifest, state):
    """Return list of shots [{type, asset_id, src, source_in/out, display, reason, ...}]."""
    rnd = state["rnd"]
    primary = state["primary"]
    sents = sentences(words)
    hits = find_entity_hits(words)
    anchors = []  # (beat_local_t, entity)
    for ent, ts in hits.items():
        for t in ts:
            anchors.append((t, ent))
    anchors.sort()
    # merge anchors closer than IMAGE_MIN_HOLD (keep first)
    merged = []
    for t, ent in anchors:
        if merged and t - merged[-1][0] < IMAGE_MIN_HOLD + 0.4: continue
        merged.append((t, ent))

    # candidate pool
    srcs = candidate_sources(beat, sources, primary)
    pool = []
    for v in srcs:
        entry = shots_index.get(v)
        if entry: pool += entry["shots"]
    if not pool:  # any primary-tag source
        for v, m in sources.items():
            if primary in m.get("subject_tags", []) and v in shots_index:
                pool += shots_index[v]["shots"]

    # build display windows across the narration span [0, vd]
    windows = []  # (t0, t1, intent, subject_named)
    if not sents:
        windows.append((0.0, vd, "build", False))
    for i, sent in enumerate(sents):
        s0, s1 = sent[0]["t"], sent[-1]["t"] + sent[-1].get("d", 0.25)
        pos = (i + 1) / len(sents)
        intent = "build" if pos < 0.6 else ("payoff" if pos >= 0.8 else "peak")
        named = any(w.get("w", "").strip().lower().strip(".,!?\"'()").replace("'s", "")
                    in ("ahyeon", "she", "her") for w in sent)
        windows.append((s0, s1, intent, named))
    # interleave image anchors -> split windows
    shots = []
    wbounds = [(w[0], w[1]) for w in windows]
    img_events = []
    for t, ent in merged:
        a = pick_image_asset(manifest, ent, state)
        if a is None:
            state["gaps"].append({"beat": beat["id"], "entity": ent, "at": round(t, 2),
                                  "note": f"no verified imagery for {ENTITY_LABEL[ent]}"})
            continue
        img_events.append((t, ent, a))
    # build final cut list: walk windows; place images inside their window
    used = state["used_shots"]; recent = state["recent_sources"]
    pref = OPENERS.get(beat.get("id"), [])

    def take_shot(t0, t1, intent, note_ctx, subject_named=False):
        need = t1 - t0
        if need < 2.0 or not pool:
            return None
        # R-v3: rank only UNUSED shots — top-8 cap previously exhausted early
        # when its members were already used elsewhere in the film
        avail = [sh for sh in pool if (sh.get("src"), sh["start"]) not in used]
        if not avail:
            return None
        ranked = sorted(avail, key=lambda sh: -score_shot(sh, need, intent, recent, used, primary, rnd,
                                                          subject_named=subject_named))
        no_video_yet = not any(s["type"] == "video" for s in shots)
        if pref and no_video_yet:
            # R-v3: opener enforcement must NOT be subject to the top-8 cap —
            # the preferred source can rank below a crowd of high-score shots
            ranked_pref = sorted([sh for sh in avail if sh.get("label") in pref],
                                 key=lambda sh: -score_shot(sh, need, intent, recent, used, primary, rnd,
                                                            subject_named=subject_named))
            for passes in ((ranked_pref, ranked), (ranked,)):
                for sh in passes[0]:
                    if sh["dur"] < min(2.0, need): continue
                    if (sh.get("src"), sh["start"]) in used: continue
                    off = sh["dur"] * (0.25 + 0.1 * rnd.random())
                    if sh["dur"] - off < need: off = max(0.0, sh["dur"] - need - 0.2)
                    use = min(need, sh["dur"] - off)
                    if use < 2.0: continue
                    used.add((sh.get("src"), sh["start"]))
                    recent.append(sh.get("label")); del recent[:-3]
                    return {"type": "video", "asset_id": sh.get("label"), "src": sh.get("src"),
                            "source_in": round(sh["start"] + off, 2),
                            "source_out": round(sh["start"] + off + use, 2),
                            "ah_score": sh.get("ah_score"), "section": sh.get("section_hint"),
                            "tags": sh.get("tags"), "reason": note_ctx or
                            f"opener — {sh.get('section_hint')} of {sh.get('label')}"}
            return None
        for sh in ranked[:8]:
            if sh["dur"] < min(2.0, need): continue
            # R-v3 (s44 bug): HARD-block shot reuse — the −4.0 penalty let weak
            # pools (dropped sources) reuse one window 4× inside a scene.
            if (sh.get("src"), sh["start"]) in used: continue
            # cut mid-shot: start 25-40% in, but keep enough tail
            off = sh["dur"] * (0.25 + 0.1 * rnd.random())
            avail_tail = sh["dur"] - off
            if avail_tail < need: off = max(0.0, sh["dur"] - need - 0.2)
            use = min(need, sh["dur"] - off)
            if use < 2.0: continue
            src_in = round(sh["start"] + off, 2)
            src_out = round(src_in + use, 2)
            used.add((sh.get("src"), sh["start"]))
            recent.append(sh.get("label")); del recent[:-3]
            return {"type": "video", "asset_id": sh.get("label"), "src": sh.get("src"),
                    "source_in": src_in, "source_out": src_out,
                    "ah_score": sh.get("ah_score"), "section": sh.get("section_hint"),
                    "tags": sh.get("tags"), "reason": note_ctx or
                    f"{intent} beat, {sh.get('section_hint')} of {sh.get('label')}"}
        return None

    cur = 0.0
    MAX_SHOT = 8.5   # editor rule: no single shot longer than ~8.5s under narration
    # map each footage span to the window (and subject flag) it falls in
    def span_intent(a, b):
        mid = (a + b) / 2
        for (w0, w1, it, named) in windows:
            if w0 <= mid < w1 or (w0 <= a and b <= w1):
                return it, named
        return ("peak", False)
    for t, ent, asset in img_events:
        hold = min(IMAGE_MAX_HOLD, max(IMAGE_MIN_HOLD, 4.0))
        t0 = max(0.0, t - 0.3)
        if t0 < cur:  # previous content overlaps anchor start; trim hold
            t0 = cur
        if t0 >= vd: continue
        # fill [cur, t0] splitting long spans into <=MAX_SHOT cuts
        while t0 - cur > 1.0:
            seg = min(MAX_SHOT, t0 - cur)
            if t0 - cur - seg > 0.0 and t0 - cur - seg < 2.2:
                seg = t0 - cur  # avoid a stubby remainder
            intent, named = span_intent(cur, cur + seg)
            shv = take_shot(cur, cur + seg, intent, None, subject_named=named)
            if not shv: break
            shv["display_start"] = round(cur, 2)
            shv["display_end"] = round(cur + seg, 2)
            shots.append(shv)
            cur += seg
        if cur >= t0 - 0.2:
            cur = t0
        tend = min(vd, t0 + hold)
        shots.append({"type": "image", "asset_id": asset.get("asset_id", ""),
                      "src": os.path.relpath(asset["file"]["path"], state["base"]),
                      "entity": ent, "license": asset.get("provenance", {}).get("license_name", ""),
                      "attribution": asset.get("provenance", {}).get("attribution", ""),
                      "display_start": round(t0, 2), "display_end": round(tend, 2),
                      "motion": "push_in" if len(shots) % 2 == 0 else "pull_out",
                      "reason": f"'{ENTITY_LABEL[ent]}' spoken at {t:.1f}s — show the place"})
        cur = tend
    while cur < vd - 0.4:
        seg = min(MAX_SHOT, vd - cur)
        if vd - cur - seg < 2.2: seg = vd - cur
        intent, named = span_intent(cur, cur + seg)
        shv = take_shot(cur, cur + seg, intent, None, subject_named=named)
        if not shv:
            # widen last shot to cover the remainder
            for sh in reversed(shots):
                if sh["type"] == "video":
                    sh["display_end"] = round(vd, 2); break
            break
        shv["display_start"] = round(cur, 2)
        shv["display_end"] = round(cur + seg, 2)
        shots.append(shv)
        cur += seg
    # post: ensure coverage has no gaps > 0.5s and no overlaps
    shots.sort(key=lambda s: s["display_start"])
    fixed = []
    for s in shots:
        if fixed and s["display_start"] < fixed[-1]["display_end"] - 0.05:
            s["display_start"] = fixed[-1]["display_end"]
        if s["display_end"] - s["display_start"] < 1.0:
            continue
        fixed.append(s)
    if fixed:
        fixed[-1]["display_end"] = round(vd, 2)
    return fixed

def plan_bg_shot(beat, shots_index, sources, primary, state):
    """Card background: one relevant shot (looping, blurred)."""
    srcs = candidate_sources(beat, sources, primary)
    pool = []
    for v in srcs:
        if v in shots_index: pool += shots_index[v]["shots"]
    if not pool: return None
    rnd = state["rnd"]
    # R-v3: card backgrounds must not double-book a shot the editor already uses
    cand = [s for s in pool if (s.get("src"), s["start"]) not in state["used_shots"]]
    if not cand: cand = pool
    sh = max(cand, key=lambda s: s.get("ah_score", 0) + rnd.random() * 0.3)
    state["used_shots"].add((sh.get("src"), sh["start"]))
    return {"type": "video", "asset_id": sh.get("label"), "src": sh.get("src"),
            "source_in": round(sh["start"] + 0.5, 2),
            "source_out": round(min(sh["end"], sh["start"] + 8.0), 2),
            "reason": "card background loop (blurred)"}

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    base = f"{BASE_ROOT}/{proj}"
    cfg = json.load(open(f"{base}/config.json"))
    target = float(cfg.get("total", 1800.0))
    fps = int(cfg.get("fps", 30))
    primary = cfg.get("primary_tag", "ahyeon")
    beats = load_beats(proj)
    timing = json.load(open(f"{base}/narration/timing.json"))
    sources = {s["video_id"]: s for s in json.load(open(f"{base}/subject_sources.json"))}
    shots_index = json.load(open(f"{base}/shots_index.json")) if os.path.exists(f"{base}/shots_index.json") else {}
    manifest = json.load(open(f"{base}/images_manifest.json")) if os.path.exists(f"{base}/images_manifest.json") else {}
    state = {"rnd": random.Random(hash(proj) & 0xffffffff), "primary": primary,
             "used_shots": set(), "recent_sources": [], "img_cursor": {},
             "gaps": [], "base": base}

    scenes, off, vd_map = [], 0.0, {}
    for b in beats:
        bid = b["id"]
        vd = round(float(timing.get(bid, {}).get("dur", 0.0)), 3)
        vd_map[bid] = vd
        kind = b["kind"]
        if kind == "card":
            ck = b["card"]["kind"]
            tail = CARD_TARGET.get(ck, 14.0)
            slot = LEAD + vd + tail
            bg = plan_bg_shot(b, shots_index, sources, primary, state)
            scene = {"id": f"s{len(scenes)+1:02d}", "beat": bid, "act": b.get("act", 0),
                     "kind": "card", "card": b.get("card"),
                     "purpose": f"{ck} card — {b.get('card', {}).get('title', ck)}",
                     "editorial_note": f"typography carries this beat; background = {'loop of ' + bg['asset_id'] if bg else 'solid brand color'}",
                     "narration": {"text": b.get("text", ""), "dur": vd},
                     "lead": LEAD, "tail": round(tail, 2), "slot": round(slot, 3),
                     "shots": ([bg] if bg else []), "music_cue": f"act{b.get('act', 0)}",
                     "captions": "word_timed", "validation": "planned"}
        elif not b.get("text", "").strip():
            slot = INTERLUDE_DUR
            shots = plan_scene_shots(b, INTERLUDE_DUR - LEAD - 2.0,
                                     words_for(base, bid) or _synth_words(INTERLUDE_DUR - LEAD - 2.0),
                                     shots_index, sources, manifest, state)
            scene = {"id": f"s{len(scenes)+1:02d}", "beat": bid, "act": b.get("act", 0),
                     "kind": "interlude",
                     "purpose": "breathing room — pure footage montage",
                     "editorial_note": "no narration; highest-presence shots, music moment",
                     "narration": {"text": "", "dur": 0.0},
                     "lead": LEAD, "tail": round(INTERLUDE_DUR - LEAD, 2),
                     "slot": round(slot, 3), "shots": shots,
                     "music_cue": f"act{b.get('act', 0)}", "captions": None,
                     "validation": "planned"}
        else:
            words = words_for(base, bid)
            tail = TAIL_CLIPS
            slot = LEAD + vd + tail
            shots = plan_scene_shots(b, vd, words, shots_index, sources, manifest, state)
            scene = {"id": f"s{len(scenes)+1:02d}", "beat": bid, "act": b.get("act", 0),
                     "kind": "clips", "purpose": beat_purpose(b),
                     "editorial_note": beat_note(b, shots, manifest),
                     "narration": {"text": b.get("text", ""), "dur": vd},
                     "lead": LEAD, "tail": tail, "slot": round(slot, 3),
                     "shots": shots, "music_cue": f"act{b.get('act', 0)}",
                     "captions": "word_timed", "validation": "planned"}
        scenes.append(scene)

    # ---- total calibration: adjust tails only (narration spacing preserved) ----
    natural = sum(s["slot"] for s in scenes)
    diff = target - natural
    if abs(diff) > 1.0:
        flex = [s for s in scenes if s["kind"] in ("clips", "interlude")]
        if diff > 0:
            wsum = sum(max(1.0, s["narration"]["dur"]) for s in flex) or 1.0
            for s in flex:
                add = diff * max(1.0, s["narration"]["dur"]) / wsum
                s["tail"] = round(min(12.0, s["tail"] + add), 2)
                s["slot"] = round(s["lead"] + s["narration"]["dur"] + s["tail"], 3)
        else:
            surplus = -diff
            for s in sorted(flex, key=lambda x: -x["tail"]):
                cut = min(surplus, max(0.0, s["tail"] - TAIL_MIN))
                s["tail"] = round(s["tail"] - cut, 2)
                s["slot"] = round(s["lead"] + s["narration"]["dur"] + s["tail"], 3)
                surplus -= cut
                if surplus <= 0: break

    # ---- frame-exact timeline ----
    frames = [round(s["slot"] * fps) for s in scenes]
    frames[-1] += fps * round(target) - sum(frames) if abs(target - sum(f / fps for f in frames)) < 30 else 0
    off = 0.0
    for s, f in zip(scenes, frames):
        s["frames"] = f
        s["dur"] = round(f / fps, 6)
        s["start"] = round(off, 4)
        s["voice_at"] = round(off + (s["lead"] if s["narration"]["dur"] > 0 else 0.0), 4)
        # shot display windows are narration-relative; keep them as-is (editor offsets)
        off += s["dur"]
    total = round(off, 3)

    plan = {"version": 2, "project": proj, "fps": fps, "target_total": target,
            "total": total, "lead": LEAD, "generator": "director.py v2",
            "seed": hash(proj) & 0xffff, "gaps": state["gaps"],
            "scenes": scenes}
    os.makedirs(f"{base}/render", exist_ok=True)
    json.dump(plan, open(f"{base}/scene_plan.json", "w"), indent=1)
    write_edit_plan_md(base, plan)
    n_shots = sum(len(s["shots"]) for s in scenes)
    n_img = sum(1 for s in scenes for sh in s["shots"] if sh["type"] == "image")
    print(f"DIRECTOR: {len(scenes)} scenes, {n_shots} shots ({n_img} context images), "
          f"total {total:.1f}s (target {target:.0f}), gaps recorded: {len(state['gaps'])}")

def _synth_words(dur):
    return [{"w": "(instrumental)", "t": 0.0, "d": dur}]

def beat_purpose(b):
    if b.get("act", 1) == 0 and b["id"].startswith("co") and b["kind"] == "clips":
        return "cold open — the hook"
    t = b.get("text", "").lower()
    if "born" in t or "chuncheon" in t: return "origin — place and childhood"
    if "notice" in t or "hiatus" in t: return "crisis — the withdrawal"
    if "debut" in t or "batter up" in t: return "event — the debut"
    if "comeback" in t or "rejoin" in t or "babymons7er" in t.replace(",", ""): return "turn — the return"
    if "charlie puth" in t or "dangerously" in t: return "proof — the voice"
    if "record" in t or "million" in t or "billboard" in t: return "scale — the numbers"
    return "development — " + (b.get("text", "")[:48].split(":")[0] or "story")

def beat_note(b, shots, manifest):
    kinds = {}
    for sh in shots:
        kinds[sh["type"]] = kinds.get(sh["type"], 0) + 1
    srcs = sorted({sh.get("asset_id", "?") for sh in shots if sh["type"] == "video"})
    ents = sorted({sh["entity"] for sh in shots if sh["type"] == "image"})
    note = f"{kinds.get('video', 0)} footage cuts from {', '.join(srcs) or 'pool'}"
    if ents: note += f"; place imagery at {', '.join(ents)}"
    if not shots: note = "no eligible shots — fallback to card (recorded gap)"
    return note

def write_edit_plan_md(base, plan):
    p = f"{base}/render/EDIT_PLAN.md"
    with open(p, "w") as f:
        f.write(f"# EDIT PLAN — {plan['project']} (director v2)\n\n")
        f.write(f"Total: {plan['total']:.1f}s (target {plan['target_total']:.0f}) · "
                f"{len(plan['scenes'])} scenes · seed {plan['seed']}\n\n")
        if plan["gaps"]:
            f.write("## Recorded gaps (policy E — no silent substitution)\n")
            for g in plan["gaps"]:
                f.write(f"- {g['beat']}: {g['note']} (at {g['at']}s)\n")
            f.write("\n")
        for s in plan["scenes"]:
            f.write(f"## {s['id']} · {s['beat']} · {s['purpose']}\n")
            f.write(f"*{s['editorial_note']}*\n\n")
            f.write(f"- start {s['start']:.1f}s · dur {s['dur']:.1f}s · "
                    f"voice at {s['voice_at']:.1f}s\n")
            if s["narration"]["text"]:
                f.write(f"- narration: \"{s['narration']['text'][:96]}...\"\n")
            for i, sh in enumerate(s["shots"]):
                if sh["type"] == "video" and "display_start" in sh:
                    f.write(f"  - {i+1}. VIDEO {sh['asset_id']} "
                            f"[{sh['source_in']:.1f}→{sh['source_out']:.1f}] "
                            f"@{sh['display_start']:.1f}-{sh['display_end']:.1f} "
                            f"(ah={sh.get('ah_score', '—')}) — {sh['reason']}\n")
                elif sh["type"] == "video":
                    f.write(f"  - {i+1}. BGSRC {sh['asset_id']} "
                            f"[{sh['source_in']:.1f}→{sh['source_out']:.1f}] — {sh['reason']}\n")
                else:
                    f.write(f"  - {i+1}. IMAGE {sh['entity']} ({sh.get('license', '?')}) "
                            f"@{sh['display_start']:.1f}-{sh['display_end']:.1f} — {sh['reason']}\n")
            f.write("\n")
    print(f"edit plan: {p}")

if __name__ == "__main__":
    main()
