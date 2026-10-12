# HARDENED RULES — last stop yt engine

These rules are NON-NEGOTIABLE. Every pipeline stage, workflow, and code path
must obey them. A violation is a build failure, not a warning.

---

## R1 — ZERO IMAGES. VIDEO ONLY. FOREVER.

> "we hate images we never ever gonna use images at all we only use videos"

1. The timeline must contain **only motion-picture sources**: downloaded video
   files, extracted character clips, or **live-rendered** graphic segments
   (ffmpeg drawtext / zoompan cards generated at render time).
2. **FORBIDDEN in the timeline:** photographs (jpg/png/webp/heic), AI-generated
   stills, stock photo stills, slideshow images, screenshots, PDF exports,
   thumbnails. Any still image asset file referenced by a timeline segment
   that is not itself a video stream is a violation.
3. The ONLY raster files allowed in a project are:
   - **face-recognition references** for character-clip-extractor (internal
     tooling input, never enters the timeline),
   - **posters/thumbnails for YouTube upload metadata only** (never in film).
4. Every render QC pass asserts `image_segments == 0` in the timeline before
   encoding. If a source is missing, the segment is dropped or replaced with
   a live-rendered card — never an image.

## R2 — SUBJECT SYNC (narration ↔ picture)

> "if the narration is talking about ahyeon the video should be ahyeon...
> never random clips"

1. Every narration segment carries `subject_tags` (canonical entity slugs,
   e.g. `blackpink`, `jennie`, `lisa`, `rose`, `jisoo`, `ygent`).
2. Every timeline segment carries the same `subject_tags`, derived from the
   provenance of its source file (which character-clip-extractor episode and
   which character it was extracted for).
3. **Hard assertion at assembly:** for every second of narration, the active
   timeline segment's subject tags must intersect the narration's tags.
   `blackpink` (group) and `ygent`/`industry` (context) are wildcard tags.
4. QC emits `subject_sync_report.json`; any mismatch fails the build.

## R3 — NARRATION VOICE

Edge TTS (`edge-tts`) is the narration engine. Voice, rate, and lexicon
(Korean name pronunciation) are fixed per project in `voice.json`.
Native per-beat SRT timestamps from edge-tts drive caption timing.

## R4 — DELIVERY SPEC (HD, YouTube-posting quality)

- 1920x1080, 30 fps, H.264 (`libx264`), CRF ≤ 18, `+faststart`, yuv420p
- Audio: AAC 192 kbps, 48 kHz, **stereo**, loudness −14 LUFS
- Duration exact to the project target (±1 s)
- QC asserts: streams, resolution, fps, audio rate/channels, duration,
  loudness, faststart atom. Any assert fails → no release.

## R5 — RESEARCH IS HARDENED INTO THE REPO

Research, dossiers, and fact ledgers are committed to the repo
(`docs/RESEARCH/`, `projects/<slug>/`), never left only in a sandbox.
Facts in narration must trace to the fact ledger with sources.

## R6 — RENDER ON RUNNERS

All heavy transcoding happens on GitHub Actions runners
(`ubuntu-latest`), never in the CPU-throttled sandbox. Workflows are
self-contained: download sources → build → QC → attach to Release.

## R7 — THE LOOP IS THE SYSTEM

One cycle produces one film:
RESEARCH → SCRIPT/NARRATION → SOURCE (video-only) → DOWNLOAD →
CHARACTER-CLIP EXTRACTION → EDITORIAL TIMELINE → VOICE/BGM/RENDER/QC.
The engine repo holds the loop; projects are state directories fed to it.
Trigger contract: `build a documentary on <subject>` must suffice.

## R8 — NO YOUTUBE DOWNLOADS ON GITHUB ACTIONS. EVER.

> "never use GitHub actions to download any yt video anymore if it's in the
> system remove it fully, use other methods all by being on your own server"

1. The former download-farm workflow (`.github/workflows/yt-download-farm.yml`)
   is REMOVED from the system. No workflow in this org may contact YouTube,
   dispatch ytagent farm methods, or transfer video from YouTube on
   GitHub-hosted runners.
2. ALL YouTube acquisition runs locally on our own server via ytagent's
   direct methods (android_vr + BGutil POT, SOCKS5 relays, Cobalt relays,
   Invidious) or character-clip-extractor's built-in downloader.
3. GitHub Actions is used ONLY for: rendering committed project state,
   QC, and attaching `final.mp4` to Releases.
