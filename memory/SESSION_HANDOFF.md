# SESSION HANDOFF — read this FIRST on every session start

## ONE-COMMAND RESUME (do this before anything else)
```bash
cd /home/z/my-project/last-stop-yt-engine && bash scripts/resume_v3.sh
```
- Self-healing: detects progress from state files, resumes where the last run died.
- Idempotent phases: env → dl → tts → plan → edit → ship.
- After EVERY download chunk it `git push`es state to branch `v3-wip`, so a
  sandbox reset loses at most one chunk of work.

## If the sandbox was reset (repo dir empty / missing)
```bash
TOK=$(tr -d ' \n' < /home/z/my-project/.ghtoken)
git clone -q "https://x-access-token:${TOK}@github.com/ansaribilal14/last-stop-yt-engine" /home/z/my-project/last-stop-yt-engine
cd /home/z/my-project/last-stop-yt-engine && git fetch origin v3-wip && git checkout v3-wip -- projects/ahyeon/ scripts/ memory/ || true
source /home/z/.venv/bin/activate && python3 -m pip install -q yt-dlp insightface opencv-python-headless onnxruntime curl_cffi
bash scripts/resume_v3.sh
```

## v3.0 build state (authoritative quick-facts)
- User's locked brief: /home/z/my-project/upload/AHYEON_x5f_DirectorsCut_x5f_v3.0_x5f_FINAL_x5f_FULL.md
  (Appendix D = link+timestamp table → Director constraints; "Final Narration v3.0"
  section at end = locked narration overrides)
- Narration overrides for s07/s23/s32/s43-44 are ALREADY APPLIED in
  projects/ahyeon/script_beats.py (verbatim from brief; Jennie purge done).
- 23 library sources: download via scripts/mirror_dl.py (state: projects/ahyeon/download_state.json)
- 12 NEW v3.0 sources (airport×5, venue×4, facecam×2, sumersonic): scripts/seek_v3.py
  (state: projects/ahyeon/download_state_v3.json)
- NETWORK FACTS (do not rediscover): YouTube/Twitter/IG/FB blocked from this IP.
  Dailymotion WORKS only with `--downloader ffmpeg` (+`--impersonate firefox`).
  vkvideo direct URLs work. Bilibili: search OK, video pages 412 → dead for download.
  yt-dlp fmt filters must not contain arithmetic (e.g. width>=height*0.9 → SyntaxError).
- Known Director bug to fix this round: window reuse (s44 used the same window 4×)
  + closeup preference — Appendix D windows are the replacement plan.
- Face gates reuse scripts/mirror_dl.py content_gate (strong/weak tiers).

## Worklog
Append progress to /home/z/my-project/worklog.md (shared across agents).
