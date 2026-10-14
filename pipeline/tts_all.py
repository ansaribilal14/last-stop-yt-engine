#!/usr/bin/env python3
"""tts_all.py — Edge TTS narration per beat (resumable, project-parameterized).
Usage: python3 tts_all.py [project] [--force]
Output: projects/<project>/narration/<beat_id>.mp3 + timing.json + <id>.words.json
Word boundaries (100ns ticks) captured for caption building.
"""
import asyncio, json, os, sys

PROJ = "blackpink"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
if ARGS: PROJ = ARGS[0]
BASE = f"/home/z/my-project/engine/projects/{PROJ}"
OUT = f"{BASE}/narration"
VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-3%"
sys.path.insert(0, "/home/z/my-project/engine/pipeline")
sys.path.insert(0, f"/home/z/my-project/engine/projects/{PROJ}")

def probe(path):
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "json", path],
                       capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

async def tts_words(text, path):
    """Edge TTS streaming: save mp3 + collect word boundaries."""
    import edge_tts, struct
    words = []
    cm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    with open(path, "wb") as f:
        async for chunk in cm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"t": chunk["offset"] / 1e7, "d": chunk["duration"] / 1e7,
                              "w": chunk["text"]})
    return words

def main():
    force = "--force" in sys.argv
    from script_beats import BEATS
    os.makedirs(OUT, exist_ok=True)
    timing = {}
    tp = f"{OUT}/timing.json"
    if os.path.exists(tp) and not force:
        timing = json.load(open(tp))
    todo = [b for b in BEATS if b["text"].strip()]
    for i, b in enumerate(todo):
        p = f"{OUT}/{b['id']}.mp3"
        wp = f"{OUT}/{b['id']}.words.json"
        if os.path.exists(p) and b["id"] in timing and os.path.exists(wp) and not force:
            continue
        try:
            words = asyncio.run(tts_words(b["text"], p))
            if os.path.exists(wp) and not force:
                pass
            json.dump(words, open(wp, "w"))
            timing[b["id"]] = {"dur": probe(p), "text": b["text"]}
            print(f"[{i+1}/{len(todo)}] {b['id']} {timing[b['id']]['dur']:.1f}s {len(words)}w", flush=True)
        except Exception as e:
            print(f"FAIL {b['id']}: {e}", flush=True)
            if os.path.exists(p): os.remove(p)
    json.dump(timing, open(tp, "w"), indent=1)
    total = sum(v["dur"] for v in timing.values())
    print(f"DONE: {len(timing)} clips, narration total {total:.1f}s", flush=True)

if __name__ == "__main__":
    main()
