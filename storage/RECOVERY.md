# RECOVERY RUNBOOK (empty-runtime → fully operational)
1. Clone repo (AGENTS.md §3). 2. If media lost: download clips_v1.zip from
release media-v1 → unzip to projects/blackpink/clips/; re-download sources via
pipeline/grind.sh (recipe committed; needs bgutil rebuilt: clone Brainicism/
bgutil-ytdlp-pot-provider → cd server → npm i typescript && tsc → node build/main.js
--port 4416; pip install yt-dlp yt-dlp-ejs edge-tts; probe_proxies.py for egress).
3. narration/ + timing.json are IN GIT → TTS never re-runs. 4. render/: rerun
assemble.py plan→segments→audio→final (resumable). 5. Verify QC probe, re-release.
