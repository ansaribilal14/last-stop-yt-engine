#!/usr/bin/env python3
"""tts_all.py — Edge TTS narration per beat (resumable).
Usage: tts_all.py            # render all missing mp3s
       tts_all.py --force    # re-render all
Output: projects/blackpink/narration/<beat_id>.mp3 + narration/timing.json
"""
import asyncio, json, os, subprocess, sys

BASE = "/home/z/my-project/engine/projects/blackpink"
OUT = f"{BASE}/narration"
VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-3%"
sys.path.insert(0, "/home/z/my-project/engine/pipeline")

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "json", path],
                       capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

async def tts(text, path):
    import edge_tts
    cm = edge_tts.Communicate(text, VOICE, rate=RATE)
    await cm.save(path)

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
        if os.path.exists(p) and b["id"] in timing and not force:
            continue
        try:
            asyncio.run(tts(b["text"], p))
            timing[b["id"]] = {"dur": probe(p), "text": b["text"]}
            print(f"[{i+1}/{len(todo)}] {b['id']} {timing[b['id']]['dur']:.1f}s", flush=True)
        except Exception as e:
            print(f"FAIL {b['id']}: {e}", flush=True)
            if os.path.exists(p): os.remove(p)
    json.dump(timing, open(tp, "w"), indent=1)
    total = sum(v["dur"] for v in timing.values())
    print(f"DONE: {len(timing)} clips, narration total {total:.1f}s", flush=True)

if __name__ == "__main__":
    main()
