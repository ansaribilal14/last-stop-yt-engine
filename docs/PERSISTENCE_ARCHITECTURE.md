# PERSISTENCE ARCHITECTURE
## Principles
Disposable runtime; Git = system of record; Releases = media of record; storage.to = delivery mirror.
## Data placement
| data | where | why |
|---|---|---|
| code, rules, research, script, narration+timing, timelines | Git (this repo) | <100MB, diffable, pull on any reset |
| clips (146, ~220MB) | Release `media-v1` (zip) + storage.to mirror | >repo limits; reharvest is 30min but download is 1min |
| source videos (1.3GB) | NOT persisted — regenerable via committed grind recipe (R8: local-only) | 43/43 repeatable |
| final films | Release per-project tag + storage.to mirror | user delivery channel |
| asset control (owner_tokens) | runtime file *.storageto.json (NOT in git — secrets) | deletion rights |
## Recovery flows
F1 empty runtime → AGENTS.md §3 startup loop. F2 media loss → ASSET_MANIFEST.json URLs first, grind second. F3 render loss → assemble.py stages resumable + narration in git. F4 session end → memory/SESSION_HANDOFF.md overwrite + worklog append + push (verified).
## Verification rule
No success claims without response verification: upload JSON (size/state), ffprobe QC, SHA-256 on a second host (Actions join step).
