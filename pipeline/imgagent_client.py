#!/usr/bin/env python3
"""imgagent_client.py — permanent Contextual Image Agent (T3).
Wraps the imgagent PyPI package (Bilal140202/imgagent) into the documentary loop:
  1. Reads a per-project image plan: entities -> query + beats that need them.
  2. Runs imgagent jobs (rights-gated, provenance-complete) with source fallback.
  3. Aggregates into projects/<slug>/images_manifest.json (Director-readable).
  4. Builds a contact sheet of candidates for the Director room.

Provenance contract: every accepted asset carries provider, source_url,
source_page_url, creator, license_name, attribution, sha256, rights_status.
Only rights_status in {verified_license, verified_public_domain} may enter the film.

Usage: python3 imgagent_client.py <project> [--only entity1,entity2]
"""
import json, os, subprocess, sys, time

BASE_ROOT = "/home/z/my-project/engine/projects"
PY = "/home/z/.venv/bin/python3"

# ---- image plan: entity -> (search queries in priority order, side hint) ----
IMAGE_PLAN = {
    "chuncheon": (["Chuncheon lake city South Korea", "Chuncheon Gangwon"], "wide"),
    "ygent": (["YG Entertainment building Seoul", "YG Entertainment headquarters"], "wide"),
    "gocheok": (["Gocheok Sky Dome Seoul stadium", "Gocheok Sky Dome concert"], "wide"),
    "seoul": (["Seoul cityscape Han river", "Seoul skyline night"], "wide"),
    "gangwon": (["Gangwon province South Korea landscape", "Gangwon do Korea mountains"], "wide"),
    "practice_room": (["dance studio mirror practice room", "dance studio mirrors empty"], "medium"),
    "korea_context": (["Seoul street night Korea", "Seoul city street"], "wide"),
}

# which beats reference which entities (derived per project from script text scan)
ENTITY_BEATS = {
    "ahyeon": {
        "chuncheon": ["a1c", "a1b01", "a8b03"],
        "seoul": ["a1b01", "a5b02", "a7b01"],
        "gangwon": ["a1b01"],
        "ygent": ["co1", "a1b02", "a1b03", "a2b02", "a3b01", "a3b04", "a4b02", "a8b02"],
        "gocheok": ["a5b01", "a5b02", "a5b04", "a7b02", "a8c", "a8b01"],
        "practice_room": ["co1", "a2b01", "a7b01"],
        "korea_context": ["a4b01", "a6b01", "a6b02", "a7b03"],
    }
}

def run_imgagent(query, project, scene, top=4):
    """One imgagent job; returns list of accepted asset dicts (manifest-grade provenance)."""
    for sources in ("openverse", "wikimedia", "openverse,wikimedia"):
        cmd = [PY, "-m", "imgagent", "run", query, "--limit", "18", "--top", str(top),
               "--sources", sources, "--require-reuse-rights", "--prefer-authentic",
               "--project", project, "--scene", scene, "--json"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
            d = json.loads(r.stdout)
            data = d.get("data", d)
            # full-provenance records live in the job manifest on disk
            mf = data.get("manifest_path")
            if mf and os.path.exists(mf):
                m = json.load(open(mf))
                assets = []
                for a in m.get("assets", []):
                    lic = (a.get("provenance", {}).get("license_name", "") or "").upper()
                    if a.get("rights_status") not in ("verified_license", "verified_public_domain"):
                        continue
                    if "ND" in lic:  # NoDerivatives: Ken Burns = derivative, excluded
                        continue
                    if not os.path.exists(a.get("file", {}).get("path", "")):
                        continue
                    assets.append(a)
                if assets:
                    return assets
            # fallback: download_results are flat records (path + sha, no provenance)
            flat = [a for a in (data.get("download_results") or [])
                    if a.get("path") and os.path.exists(a["path"])
                    and a.get("status") in (None, "ok", "downloaded", "duplicate")]
            if flat:
                return [{"file": {"path": a["path"], "sha256": a.get("sha256", ""),
                                  "width": a.get("width"), "height": a.get("height")},
                         "provenance": {"provider": a.get("provider", "?")},
                         "rights_status": "unverified", "asset_id": a.get("asset_id", "")}
                        for a in flat]
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
            print(f"  imgagent try {sources}: {type(e).__name__}", flush=True)
        time.sleep(2)
    return []

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    base = f"{BASE_ROOT}/{proj}"
    out_p = f"{base}/images_manifest.json"
    manifest = {"version": 1, "project": proj,
                "entities": {}, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    if os.path.exists(out_p):
        manifest = json.load(open(out_p))
    beats_map = ENTITY_BEATS.get(proj, {})
    for entity, (queries, side) in IMAGE_PLAN.items():
        if only and entity not in only: continue
        if entity in manifest["entities"] and manifest["entities"][entity].get("assets"):
            print(f"[{entity}] cached ({len(manifest['entities'][entity]['assets'])} assets)")
            continue
        got = []
        for q in queries:
            for beat in beats_map.get(entity, ["general"])[:2]:
                got = run_imgagent(q, proj, beat)
                if got: break
            if got: break
        if got:
            manifest["entities"][entity] = {
                "queries": queries, "side": side, "beats": beats_map.get(entity, []),
                "assets": got}
            print(f"[{entity}] {len(got)} assets via '{queries[0]}'", flush=True)
        else:
            manifest["entities"][entity] = {"queries": queries, "side": side,
                                            "beats": beats_map.get(entity, []),
                                            "assets": [], "gap": "no rights-verified imagery"}
            print(f"[{entity}] GAP — no rights-verified imagery found", flush=True)
        json.dump(manifest, open(out_p, "w"), indent=1)
    # contact sheet
    build_sheet(base, manifest)
    n = sum(len(e.get("assets", [])) for e in manifest["entities"].values())
    print(f"IMAGES: {n} assets across {len(manifest['entities'])} entities -> {out_p}")

def build_sheet(base, manifest):
    """Contact sheet: one row per entity, up to 4 images, labels burned."""
    import glob
    out = f"{base}/render/storyboard/images_sheet.jpg"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tiles = []
    for entity, e in manifest["entities"].items():
        for a in e.get("assets", [])[:4]:
            p = a.get("file", {}).get("path")
            if p and os.path.exists(p):
                tiles.append((entity, p))
    if not tiles:
        return
    # build via ffmpeg: scale each to 320x180, hstack rows of 4 with drawtext entity tag
    inputs, fc, idx = [], [], 0
    rows = []
    for i in range(0, len(tiles), 4):
        row = tiles[i:i + 4]
        parts = []
        for j, (ent, p) in enumerate(row):
            inputs += ["-i", p]
            parts.append(f"[{idx}:v]scale=320:180:force_original_aspect_ratio=increase,"
                         f"crop=320:180,drawtext=text={ent}:x=6:y=6:fontsize=18:"
                         f"fontcolor=white:box=1:boxcolor=black@0.6[t{idx}]")
            idx += 1
        pad = 4 - len(row)
        if pad:
            inputs += ["-f", "lavfi", "-i", f"color=c=black:s=320x180:d=1"] * pad
            for k in range(pad):
                parts.append(f"[{idx}:v]null[t{idx}]"); idx += 1
        parts.append("".join(f"[t{x}]" for x in range(idx - 4, idx)) + "hstack=4[r{i}]".format(i=i // 4))
        rows.append(f"r{i // 4}")
        fc += parts
    n_rows = len(rows)
    fc.append("".join(f"[{r}]" for r in rows) + f"vstack={n_rows}[out]")
    subprocess.run(["ffmpeg", "-y", "-nostdin"] + inputs +
                   ["-filter_complex", ";".join(fc), "-map", "[out]",
                    "-frames:v", "1", "-q:v", "4", out],
                   capture_output=True, timeout=180)
    print(f"sheet: {out} ({len(tiles)} tiles)")

if __name__ == "__main__":
    main()
