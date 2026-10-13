# AGENTS.md — PERMANENT AGENT OPERATING CONTRACT (git-centric, reset-proof)

> This file is the single source of truth for agent behaviour. It survives every
> runtime reset because it lives in Git (ansaribilal14/last-stop-yt-engine).
> On ANY session start, execute "STARTUP RECOVERY" below BEFORE taking user tasks.

## 1. Identity & keys (rotate on leak; never commit secrets)
- GitHub account: `ansaribilal14` (token supplied per-session by user; scopes repo+workflow)
- Git identity: `ansaribilal14@users.noreply.github.com`
- Remote push form: `https://ansaribilal14:<TOKEN>@github.com/ansaribilal14/<repo>.git`
- TTS: edge-tts (`pip install edge-tts` into the ACTIVE venv `/home/z/.venv`)
- POT server: bgutil (rebuild recipe in `pipeline/grind.sh` header + storage/RECOVERY.md)

## 2. Hardened rules (R1–R8, full text in HARDENED_RULES.md)
R1 zero still images, video-only · R2 narration/subject sync · R3 Edge TTS ·
R4 HD spec (1080p30 H.264, AAC 192k 48kHz stereo, −14 LUFS, faststart) ·
R5 research hardened into repo before build · R6 re-render via runner only ·
R7 single loop system · **R8 GitHub Actions NEVER downloads YouTube; acquisition is local-only.**

## 3. Startup recovery (execute in order, every session)
1. Read `worklog.md` last 3 sections (runtime path `/home/z/my-project/worklog.md`)
2. `git clone https://ansaribilal14:<TOKEN>@github.com/ansaribilal14/last-stop-yt-engine.git /home/z/my-project/engine` (if missing)
3. Read `memory/CURRENT_STATE.md` + `memory/SESSION_HANDOFF.md` → resume the marked stage
4. Rebuild media if `ytdl_cache/`/`clips/` are empty: prefer `storage/ASSET_MANIFEST.json`
   URLs (download clips zip from release) over re-probing proxies; fall back to
   `pipeline/grind.sh` (recipe is committed and repeatable)
5. Verify tools: `python3 -m yt_dlp --version`, `edge_tts`, bgutil ping :4416

## 4. Write discipline (LESSON PAID FOR IN LOST WORK)
- **Commit + push after EVERY artifact.** Verify pushes: never pipe `git push`
  through `tail`/`&&` chains that mask exit codes. Use
  `git push origin main > /tmp/push.log 2>&1; echo EXIT=$?` and check the log.
- Small durable state (narration mp3s, timing.json, timeline.json) is committed
  INTO the repo. Large media goes to Release assets (clips zip ≤2GiB, final films).
- Background processes die at tool boundaries. Never `&`-detach. Use
  concurrent foreground work + `wait` inside ONE call for parallelism.

## 5. Asset persistence (spec: storage.to + GitHub Releases)
- Every completed asset is IMMEDIATELY (a) uploaded via `pipeline/upload_storageto.py`
  (3-step presigned multipart API per storage.to docs) and (b) attached to a GitHub
  Release. Record BOTH in `storage/ASSET_MANIFEST.json` with SHA-256 + owner_token file.
- Deletions (user-requested expiry) MUST be logged in `storage/DELETION_LOG.md`.
- Never claim an upload succeeded without verifying the response (size/state/SHA).

## 6. Project lifecycle
S0 research → S1 dossier+facts (commit) → S2 source map (commit) → S3 download
grind (local, R8) → S4 harvest clips (commit sidecars, zip to release) →
S5 script+TTS (commit) → S6 render (runner-eligible, R6) → S7 QC assert →
S8 release + manifest update. Each stage: worklog entry + git push.
