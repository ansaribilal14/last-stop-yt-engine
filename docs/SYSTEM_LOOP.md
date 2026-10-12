# SYSTEM_LOOP — the unified cycle of last stop yt engine

One loop, seven stages, one film. Every stage reads and writes state inside
`projects/<slug>/` and leaves sentinels so an interrupted run resumes.

```
S1 RESEARCH ──▶ S2 SCRIPT/NARRATION ──▶ S3 SOURCE MAP ──▶ S4 DOWNLOAD
                                                                  │
   RENDER/QC ◀── S6 EDITORIAL TIMELINE ◀── S5 CHARACTER CLIPS ◀──┘
        │
        └─▶ Release (final.mp4) ──▶ YouTube-ready
```

## Stage contracts

| Stage | Input | Output (state) | Tooling | Hardened rule |
|---|---|---|---|---|
| S1 research | subject | `dossier.md`, `facts.json` (sources per fact) | web research + NIM QA | R5: committed to repo |
| S2 script | dossier | `script.json` (67+ beats, each with `subject_tags`) | NIM LLM, fact-gated | R2: tags mandatory |
| S3 source map | script | `subject_sources.json` (entity → candidate YouTube sources w/ licenses) | catalog + search | R1: video-only sources |
| S4 download | source map | `ytdl_cache/<id>.mp4` (verified) | **ytagent** (13-method chain, BGutil POT) | R6: verify A/V parity |
| S5 extraction | downloads | `<character>_FULL_<id>.mp4` + `timeline.json` per episode | **character-clip-extractor** (InsightFace) | R2: provenance tagged |
| S6 editorial | clips + script | `timeline.json` (segment list, subject-synced) | assembly + R2 assertions | R1: image_segments == 0 |
| S7 render | timeline + voice | `final.mp4` + QC report | edge-tts + ffmpeg + Actions | R3, R4: spec + QC asserts |

## Integration map (the 17 repositories)

| Repo | Role in the loop | Status |
|---|---|---|
| ansaribilal14/character-clip-extractor | S5 — subject-true clip extraction (CRF16, one full per-episode video, resume) | **CORE** |
| ansaribilal14/ytagent (mirror of Bilal140202/ytagent) | S4 — verified downloads, 13-method fallback, datacenter-IP bypass | **CORE** |
| Bilal140202/ttagent · igagent · xthread-agent | optional research/monitoring agents (TikTok/IG/Threads scouting) | AUX |
| ansaribilal14/personal-social-agent | publishing/ops auxiliaries | AUX |
| ansaribilal14/uaal | agent utilities | AUX |
| ahyeon-documentary (restored) | proven production code: render, NIM QA, workflows, brand system | **INHERITED** |
| documentary-agent-kit (restored) | agent contracts, 8-beat structure, fact-researcher/media-scout subagents | **INHERITED** |
| last-stop-archive | research corpus + dossiers (private backup) | **INHERITED** |
| babymonster-documentary-pipeline | group-doc reference architecture | REF |
| open-video-engine (+web/android) | render engine reference | REF |
| somerton-man-documentary, opuscar-studio, vfactory, films, imgagent, promos | prior production patterns (image-era — R1 forbids their image paths) | REF |
| edenfunf/reelmimic (private mirror) | editing-pattern reference | REF |
| ChatCut-Inc/agent-plugin (private mirror) | agentic editing contract reference | REF |

## Non-sequential editing (S6 is a real editor, not a playlist)

S6 assembles the film the way an editor would:
1. **Cold open** — strongest hook beat, out of chronological order.
2. **Beat map** — acts/beats from script.json drive structure; pacing varies
   (long analytic takes vs rapid stat cuts), J-cuts between narration and
   next segment's audio bed.
3. **Subject-sync assembly** — segment pool per beat is chosen from S5
   outputs whose `subject_tags` intersect the beat's tags; the R2 assertion
   runs per-second before any render.
4. **Visual rhythm** — no segment longer than 20 s without a cut; motion
   cards (live-rendered) only for stats/quotes/chapters.
5. **BGM bed** — CC0/licensed track, sidechain-ducked −12 dB under voice,
   −14 LUFS master.
