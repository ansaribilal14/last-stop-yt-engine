# CURRENT STATE (authoritative, update at every stage end)
- DATE: 2026-10-15 · PROJECT: ahyeon ("Ahyeon — The 5th Gen It Girl")
- STATUS: **DELIVERED v2.0-ahyeon (Director's Cut)** — editorial overhaul complete
  https://github.com/ansaribilal14/last-stop-yt-engine/releases/tag/v2.0-ahyeon
  final.mp4 1379585365B · 1800.07s (30:00) · 1080p30 · AAC 192k 48k stereo · -14 LUFS · captions burned
- v1.0-ahyeon deleted (user-permitted) before v2.0 publish.
- SYSTEM v3 (all issues #1-#11 closed):
  1. Verified acquisition: scripts/mirror_dl.py (title gate + strong/weak face-content gate +
     DM discovery + per-source budgets). 23/24 sources; dome_fancam dropped w/ reason.
     ⚠ ALL sources genpts-normalized; DM FixupM3U8 files (nextmovement/hotsauce/batterup_stage)
     FULLY RE-ENCODED — they deadlock ffmpeg multi-input concat otherwise.
  2. Shot index: 1692 shots / 23 sources (scdet) + face scores on ALL shots
     (faceverify v3: segmented kill-safe, largest-face-only, landmark models skipped).
  3. Contextual images: 15 rights-verified plates (7 entities) via imgagent_client;
     ygent = recorded gap (policy E).
  4. Director v2.1: scene_plan.json EDL — 48 scenes / 167 shots / 12 image placements,
     word-level entity anchoring, subject-named-sentence closeup preference, exact 1800.0s.
  5. Editor (assemble v3): EDL executor — real timecode trims, crop-pan KB cache,
     atomic .tmp.mp4 segs, per-scene resume. NO randomness anywhere.
  6. QA: qa_sync.py + qa_ahyeon_claims.py (5/20 verified closeups at spoken mentions,
     9 group/wide, 2 likely, 4 no-face = cards/backlit wide — visually reviewed).
- KNOWN LIMITS: corr metric false-alarms on night plates (human-reviewed correct);
  interview ah=weak tier (drifted embeddings, real footage); sandbox CPU throttling varies.
- Pending: none. User may revoke GH token after use.
