#!/usr/bin/env python3
"""score_build.py — composed documentary score via opuscar CC0 sampler (48k stereo).

Replaces the old sine-drone bed (source of audible distortion) with real
instrument cues aligned to the film's act structure.

Usage:
    score_build.py <project>          # build projects/<project>/render/bed.wav

Reads   projects/<project>/render/cues.json:
    {"total": 1800.0,
     "cues": [{"t0": 0, "t1": 95, "preset": "overture", "intensity": 0.55,
               "root": "D3", "minor": true}, ...]}
Writes  projects/<project>/render/bed.wav   (stereo float32 @48k, mastered)

Preset recipes (documentary):
  overture  strings pad + piano motif + low strings, builds
  trainee   sparse piano + soft strings (hopeful, restrained)
  tension   tremolo-ish strings + timpani swells + low drone bass
  dark      low strings only, slow, heavy (hiatus)
  dawn      piano + glockenspiel + strings opening up
  triumph   full strings + horns + tubular bells
  warm      vibraphone + piano + strings, major, gentle
  resolve   piano + slow strings, final cadence

Music core vendored from lemo-opuscar (MIT). Piano = Salamander (CC BY 3.0,
credits emitted via sampler.credits -> credits.txt).
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sampler as S
from sfx import SR, limit

XFADE = 2.5          # cue crossfade seconds
TAIL = 4.0           # instrument release tail room

# roman-numeral progressions (semitone offsets from root, quality per chord)
PROGS = {
    "overture": [(0,"m"),(8,"M"),(3,"M"),(10,"M")],
    "trainee":  [(0,"M"),(7,"M"),(9,"m"),(5,"M")],
    "tension":  [(0,"m"),(0,"m"),(8,"M"),(7,"m")],
    "dark":     [(0,"m"),(7,"m"),(8,"M"),(5,"m")],
    "dawn":     [(0,"M"),(9,"m"),(5,"M"),(7,"M")],
    "triumph":  [(0,"M"),(7,"M"),(5,"M"),(0,"M")],
    "warm":     [(0,"M"),(4,"m"),(5,"M"),(0,"M")],
    "resolve":  [(0,"M"),(5,"M"),(0,"M"),(7,"M")],
}

def chord_notes(root_midi, semi, quality):
    """root-position triad midi notes."""
    third = 4 if quality == "M" else 3
    return [root_midi + semi, root_midi + semi + third, root_midi + semi + 7]

def events_for_cue(cue, dur):
    """Event list for one cue. Bars of ~8s; voices per preset."""
    p = cue["preset"]; inten = float(cue.get("intensity", 0.5))
    minor = bool(cue.get("minor", p in ("overture","tension","dark")))
    root = S.midi(cue.get("root", "D3" if minor else "C4"))
    prog = PROGS.get(p, PROGS["overture"] if minor else PROGS["dawn"])
    ev, t, bar = [], 0.0, 8.0
    ci = 0
    while t < dur:
        d = min(bar, dur - t)
        semi, q = prog[ci % len(prog)]
        # voicing: pad triad + octave
        tri = chord_notes(root, semi, q)
        pad = [tri[0]-12, tri[0], tri[1], tri[2]]
        rnd = np.random.default_rng(int(t * 7 + ci * 13 + len(p)))
        # string pad (always) — violins/violas/celos split
        if p != "dark":
            for j, n in enumerate(pad):
                ev.append(dict(t=t, inst="violins" if n >= root+7 else ("violas" if n >= root else "cellos"),
                               pitch=float(n), dur=d + 1.5, vel=0.30 + 0.16 * inten,
                               pan=(-.35 + .7 * j / max(1, len(pad) - 1)),
                               attack=(0.9 - 0.4 * inten) + 0.25 * rnd.random()))
        # low strings / bass
        ev.append(dict(t=t, inst="contrabass", pitch=float(tri[0]-24 if tri[0]-24 >= 26 else tri[0]-12),
                       dur=d + 1.0, vel=0.34 + 0.20 * inten, pan=0.0,
                       attack=0.5 + 0.5 * rnd.random()))
        if p in ("tension", "dark"):
            # breathing low cello swell + timpani heartbeat
            ev.append(dict(t=t, inst="cellos", pitch=float(tri[0]-12), dur=d*0.9, vel=0.38+0.2*inten,
                           pan=-.15, attack=d*0.45))
            if p == "tension" and ci % 2 == 0:
                ev.append(dict(t=t + d*0.5, inst="timpani", pitch='D3' if ci % 4 == 0 else 'G3',
                               vel=0.30 + 0.25 * inten, dur=2.0))
        # piano motif
        if p in ("overture", "trainee", "dawn", "warm", "resolve") and (ci % 2 == 0 or inten > 0.6):
            mel = [tri[2] + 12, tri[1] + 12, tri[0] + 12, tri[1] + 12]
            mt = t + d * 0.5 if p in ("trainee", "warm") else t
            for k, n in enumerate(mel[:2 if p == "trainee" else 4]):
                if rnd.random() < 0.85:
                    ev.append(dict(t=mt + k * (d / 6.0), inst="piano", pitch=float(n),
                                   dur=1.2, vel=0.30 + 0.30 * inten, pan=0.18 * (1 if k % 2 else -1)))
        # mallet sparkle
        if p in ("dawn", "triumph", "warm") and ci % 2 == 1:
            spark_inst = "glockenspiel" if p in ("dawn", "triumph") else "vibraphone"
            for k, n in enumerate(tri):
                ev.append(dict(t=t + d*0.5 + k * 0.55, inst=spark_inst, pitch=float(n + 12),
                               dur=1.6, vel=0.22 + 0.22 * inten, pan=(-.4 + .4 * k)))
        # brass + bells on triumph
        if p == "triumph":
            ev.append(dict(t=t, inst="horn", pitch=float(tri[0]), dur=d*0.85, vel=0.30 + 0.25*inten,
                           pan=-.2, attack=0.8))
            if ci % 2 == 0:
                ev.append(dict(t=t, inst="tubular_bells", pitch=float(tri[2] + 12), dur=2.5,
                               vel=0.30 + 0.2 * inten, pan=.3))
        if p == "tension" and ci % 4 == 3:
            ev.append(dict(t=t + d*0.9, inst="gran_cassa", pitch='roll', vel=0.35 + 0.3*inten))
        t += bar; ci += 1
    return ev

def render_cue(cue):
    t0, t1 = float(cue["t0"]), float(cue["t1"])
    dur = t1 - t0
    S.seed(1000 + int(t0))
    ev = events_for_cue(cue, dur)
    buf = S.render(ev, dur=dur + TAIL, master=True)
    rev_size = {"dark": .62, "tension": .55, "triumph": .5}.get(cue["preset"], .45)
    buf = S.room(buf, size=rev_size, mix=.14)
    # equal-power cue crossfades
    n = len(buf); tt = np.arange(n) / SR
    fin = np.minimum(1.0, tt / XFADE); fout = np.clip((n / SR - tt) / XFADE, 0, 1)
    buf *= (np.sin(fin * np.pi / 2) * np.sin(fout * np.pi / 2))[:, None].astype(np.float32)
    return t0, buf.astype(np.float32)

def master(canvas):
    # gentle low-shelf tame: kill <32Hz rumble (old bed's distortion band)
    from scipy.signal import butter, sosfilt
    for ch in range(2):
        canvas[:, ch] = sosfilt(butter(2, 32, "high", fs=SR, output="sos"), canvas[:, ch])
        canvas[:, ch] = limit(canvas[:, ch].astype(np.float64), .88).astype(np.float32)
    return canvas

def main():
    project = sys.argv[1] if len(sys.argv) > 1 else "ahyeon"
    BASE = f"/home/z/my-project/engine/projects/{project}"
    cfg = json.load(open(f"{BASE}/render/cues.json"))
    total = float(cfg["total"])
    os.makedirs(f"{BASE}/render", exist_ok=True)
    out_path = f"{BASE}/render/bed.wav"
    N = int(round(total * SR))
    canvas = np.zeros((N, 2), np.float32)
    for k, cue in enumerate(cfg["cues"]):
        t0, buf = render_cue(cue)
        s = int(t0 * SR); e = min(N, s + len(buf))
        canvas[s:e] += buf[:e - s]
        peak = float(np.abs(buf).max())
        print(f"cue {k}: {cue['preset']:8s} {cue['t0']:7.1f}-{cue['t1']:7.1f} peak {peak:.3f}", flush=True)
        del buf
    canvas = master(canvas)
    peak = float(np.abs(canvas).max())
    canvas *= min(1.0, 0.72 / max(peak, 1e-6))
    import soundfile as sf
    sf.write(out_path, canvas, SR, subtype="FLOAT")
    rms = float(np.sqrt((canvas ** 2).mean()))
    print(f"bed.wav written: {total:.1f}s peak {peak:.3f} rms {20*np.log10(rms+1e-9):.1f} dBFS")
    with open(f"{BASE}/render/music_credits.txt", "w") as f:
        f.write("\n".join(S.credits(["piano", "cellos", "violins", "violas",
                                     "contrabass", "horn", "glockenspiel",
                                     "vibraphone", "tubular_bells", "timpani"])) + "\n")

if __name__ == "__main__":
    main()
