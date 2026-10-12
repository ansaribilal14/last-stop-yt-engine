# last stop yt engine

**The last video engine you will ever need.** One command in, a finished
HD YouTube documentary out — real footage, zero images, narration perfectly
synced to the subject on screen.

```
build a documentary on Jennie Kim
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  S1 research → S2 script → S3 sources → S4 download         │
│        → S5 character clips → S6 editorial → S7 render/QC   │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
   final.mp4 — 1080p H.264 · AAC 192k 48kHz stereo · −14 LUFS
```

## What this is

A unified documentary production loop that hardens seven stages into one
system. It inherits the proven production code of the delivered
`ahyeon-documentary` (29:00 film, QC PASS) and integrates the tool fleet:

- **ytagent** — verified YouTube downloads (13-method fallback, datacenter-IP
  bypass via BGutil POT).
- **character-clip-extractor** — subject-true extraction: feed an episode and
  a character, get every scene of that character as one full video (CRF16,
  auto-resume, CPU-only InsightFace).
- **NIM LLM QA** — fact-gated scripting with an automated slop/QA pass.
- **edge-tts** — narration with native SRT timestamps.
- **GitHub Actions** — all heavy render on runners; QC-gated releases.

## The two laws

1. **ZERO IMAGES.** The timeline contains only real video footage and
   live-rendered motion cards. Never a photograph. Ever.
2. **SUBJECT SYNC.** If narration says Ahyeon, the screen shows Ahyeon.
   Per-second assertions enforce it before any pixel is encoded.

Full contract: [`HARDENED_RULES.md`](HARDENED_RULES.md) ·
Loop architecture: [`docs/SYSTEM_LOOP.md`](docs/SYSTEM_LOOP.md)

## Usage

```bash
# inside the engine checkout
python3 pipeline/build.py --project projects/<slug>        # local (small steps)
# or trigger the one-click render (heavy steps on runners):
gh workflow run render.yml -f project=<slug>
```

Artifacts land in the repo's Releases as `final.mp4` (QC PASS only).

## First mission

`projects/blackpink/` — **"Why there will be no next BLACKPINK"**
Target: 34:00 ultra documentary, HD, YouTube-posting quality.
Brief: [`projects/blackpink/BRIEF.md`](projects/blackpink/BRIEF.md)
