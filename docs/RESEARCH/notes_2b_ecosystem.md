# Task 2-b Research Notes — Documentary Agent Ecosystem

## Verified by direct fetch/test in sandbox
- agents.md site (https://agents.md/): open format, "README for agents", 60k+ projects; adopters incl. OpenAI Codex, Cursor, Jules, Factory, Aider, goose, opencode, Zed, Warp, VS Code, Devin, Gemini CLI, GitHub Copilot coding agent. Popular sections: project overview, build/test commands, code style, testing instructions, security; nested AGENTS.md per package (nearest file wins). Sample file in repo openai/codex.
- anthropics/skills README: skills = folders with SKILL.md (YAML frontmatter name+description), optional scripts/resources; register as plugin marketplace `/plugin marketplace add anthropics/skills`; spec at ./spec + agentskills.io; template skill included. Apache 2.0 for most; docx/pptx/xlsx/pdf skills source-available.
- agentskills.io: skill folder layout SKILL.md + scripts/ + references/ + assets/; progressive disclosure: Discovery (name+description loaded at startup) → Activation (full SKILL.md) → Execution (bundled code).
- vercel-labs/skills README: `npx skills add owner/repo`, `npx skills use repo@skill --agent claude-code`; npm package `skills`; supports 75+ agents (Claude Code, Codex, Cursor, OpenCode...). skills.sh registry.
- Claude Code subagents (docs.claude.com/en/docs/claude-code/sub-agents.md fetched, 108KB): files in `.claude/agents/` (project) or `~/.claude/agents/` (user); frontmatter example:
```
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---
You are a code reviewer...
```
  Body = system prompt. Fields incl. model, tools, isolation: worktree, omitClaudeMd. Built-ins: Explore (read-only), Plan, general-purpose. Descriptions kept short (15k token total warning).
- API probes from sandbox:
  - Openverse `https://api.openverse.org/v1/images/?q=...` → 200 OK keyless (result_count 240 for kangaroo). Anonymous limit ~20 req/min, 200 req/day (GitHub issue #5315); auth raises it.
  - NASA `https://images-api.nasa.gov/search?q=apollo+11&media_type=image` → 200 OK keyless.
  - Wikimedia Commons action API `action=query&list=search&srsearch=apollo filetype:video&srnamespace=6` → 200 OK keyless; found "File:Apollo 15 feather and hammer drop.ogv" (totalhits 382). No auth; shared polite limit ~200 req/s.
  - Internet Archive advancedsearch/metadata endpoints TIMED OUT from sandbox (network); endpoints documented: `/advancedsearch.php?q=...&fl[]=identifier&rows=N&output=json`, `/metadata/{id}`.
  - Pexels: 401 without key ("Missing API key"); free 200 req/hr + 20k/mo (help.pexels.com).
  - Pixabay: `[ERROR 400] Invalid or missing API key`; free; 100 req/60s (pixabay.com/api/docs).
  - Unsplash: OAuth error without token; demo 50 req/hr.
  - Freesound: token auth; 60 req/min + 2000/day standard (freesound.org/docs/api/overview.html).

## TTS verified
- edge-tts (rany2/edge-tts README fetched): pip install edge-tts; CLI `edge-tts --text ... --write-media hello.mp3 --write-subtitles hello.srt` — produces SUBTITLES natively. Free (uses Edge online service), 400+ voices, 90+ languages incl. hi-IN, ko-KR (via TTS_NO_API repo list).
- kokoro (hexgrad/kokoro README): 82M params, Apache weights, pip install kokoro, quality comparable to larger models; kokoro-onnx for ONNX runtime. v1.0 langs: en, ja, zh, es, fr, hi, it, pt (en-us/en-gb accents).
- F5-TTS (SWivid README fetched): DiT w/ ConvNeXt V2, v1 base 2025-03; MIT code, CC-BY-NC weights.
- fish-speech (fishaudio README fetched): S2 Pro flagship; codebase + weights under FISH AUDIO RESEARCH LICENSE (non-commercial); 80+ languages, 15k+ style tags.
- ElevenLabs: multilingual v2 most lifelike; Flash/Turbo v2.5 $0.04–0.10/1k chars API; free tier ~10k credits; supports Hindi+Korean (v2/v2.5 multilingual).
- OpenAI TTS: gpt-4o-mini-tts ≈$0.015/min (0.60/1M input + $12/1M audio tokens); tts-1/tts-1-hd legacy. 11 voices, multi-lang.
- Cartesia: Sonic 3.6; from $5/mo; ~1 credit/char standard TTS; < $15/M chars at volume; top leaderboard scores.
- XTTS v2 (Coqui): Coqui company shut down 2024; model on HF; CPML license (non-commercial); multilingual incl. hi, ko... (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh, ja, hu, ko, hi).

## Captions
- faster-whisper (SYSTRAN README): word_timestamps=True confirmed in README code; Silero VAD; batched pipeline; large-v3 <8GB GPU.
- whisperX (m-bain README): 70x realtime large-v2, word-level via forced alignment, diarization.
- Karaoke route: Whisper word timestamps → ASS `\k` tags → FFmpeg `ass` filter (ffmpeg-micro.com article); repos: nikhil-reddy05/auto-captions, nicolaigaina/ai-video-captions (faster-whisper → animated ASS → burn-in).

## Music
- AudioCraft/MusicGen: code MIT, WEIGHTS CC-BY-NC 4.0 (non-commercial) — verified in README License section. MusicGen small/medium/large + melody.
- Stable Audio Open (stabilityai/stable-audio-tools): open weights (Stability AI Community License), 47s max, SFX+music; runs on GPU.
- Pixabay Music: free key, same 100/min API (music endpoint `/api/music/` on paid... actually pixabay.com/api/music/ works w/ key), no attribution, Content License.
- FMA (Free Music Archive): curated CC-licensed tracks; API deprecated — manual/JSON catalog download.

## YouTube upload
- videos.insert = 1600 quota units; default project quota 10,000/day → ~6 uploads/day (postproxy.dev, codewords.ai, getphyllo.com). Resumable upload w/ MediaFileUpload chunk; OAuth desktop flow (InstalledAppFlow) via google-api-python-client; videos must be private/unlisted-then-public workaround for API uploads to skip verification for unverified apps. Metadata: title (≤100 chars), description (chapters need ≥3 timestamps, first 00:00), tags ≤500 chars, categoryId, thumbnail.set (separate call, requires verified account).

## Reference projects
- MoneyPrinterTurbo (README fetched): stages = subject/keyword → LLM script (many providers) → assets (Pexels/Pixabay/Coverr/local + AI txt2video) → TTS (Edge TTS default free; Azure V2, SiliconFlow, Gemini TTS, ElevenLabs, Kokoro, Chatterbox, Fish Audio...) → subtitles (edge timestamps or faster-whisper large-v3/turbo) → FFmpeg/MoviePy composite → (upload separate). WebUI+API+CLI+Agent modes. Short-form focus.
- ShortGPT: framework w/ "LLM-oriented video editing language" (Automated Editing Framework), asset sourcing, voiceover (multi-lang), auto-edit; web app + Colab.
- NarratoAI: LLM film-recap/commentary tool: script + auto editing + dubbing + subtitles; works on PROVIDED footage, not sourcing.
- MoneyPrinterV2: money-making automation: YT Shorts automator w/ CRON scheduler, Twitter bot, affiliate; modular rewrite.

## Fact layer
- Perplexica (README fetched): open-source Perplexity; SearxNG backend; cited sources; local LLMs (Ollama) + cloud; modes (Speed/Balanced/Quality).
- Tavily: free 1,000 credits/mo, then $0.0075–0.008/credit (tavily.com/pricing, docs).
- Serper: Google SERP API, 2,500 free queries on signup (exa.ai blog).
- Wikipedia REST summary + action API extracts — verified working in project earlier (Task 1 env notes). Wikidata SPARQL at query.wikidata.org keyless.

## YouTube policy
- "Repetitious content" renamed "inauthentic content" (July 2025), mass-produced/repetitive ineligible for monetization (support.google.com/youtube/answer/1311392). AI narration alone not disqualifying; template mass production is. Content ID claims on non-cleared archival footage; use PD/CC sources + attribution; keep license ledger.
