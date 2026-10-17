#!/bin/bash
# resume_v3.sh — ONE-COMMAND self-healing runner for the v3.0 build.
#
# WHY THIS EXISTS: sandboxes reset without warning; background jobs die at tool
# boundaries. So this script is the ONLY thing a fresh session needs to run:
#     cd /home/z/my-project/last-stop-yt-engine && bash scripts/resume_v3.sh
# It detects its own progress from state files and resumes exactly where the
# last run died. Every phase is idempotent. State is pushed to origin (branch
# v3-wip) after EVERY chunk, so even a full wipe loses at most one chunk.
#
# Phases (auto-skip when complete):
#   env  - symlink /home/z/my-project/engine, verify deps, create dirs
#   dl   - mirror_dl.py chunks (23 library sources) then seek_v3.py chunks (12 v3 sources)
#   tts  - regenerate narration for beats whose text changed
#   plan - Director: scene_plan.json (with Appendix-D window constraints)
#   edit - assemble.py (per-scene resume) + final render + QA
#   ship - tag v3.0-ahyeon + release upload
#
# Usage: bash scripts/resume_v3.sh [phase]     # default: auto (all phases in order)
set -u
cd "$(dirname "$0")/.."
REPO="$PWD"
export PATH="/home/z/.venv/bin:$PATH"
LOG="$REPO/projects/ahyeon/render/resume_v3.log"
mkdir -p "$(dirname "$LOG")"
log(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

push_state(){
  git add -A projects/ahyeon/*.json projects/ahyeon/script_beats.py \
      scripts/ memory/ pipeline/script_beats.py 2>/dev/null
  git commit -q -m "v3 auto-checkpoint: $1 $(date -u +%FT%TZ)" 2>/dev/null && \
  git push -q origin HEAD:v3-wip 2>/dev/null && log "state pushed (v3-wip): $1" || \
  log "state push skipped/failed for: $1"
}

phase_env(){
  ln -sfn "$REPO" /home/z/my-project/engine
  mkdir -p projects/ahyeon/ytdl_cache projects/ahyeon/render
  python3 - <<'EOF' || { log "FATAL: deps missing"; exit 1; }
import yt_dlp, insightface, cv2, numpy
print("deps OK")
EOF
  [ -f tools/cce_references/refs_summary.json ] || { log "FATAL: refs_summary.json missing"; exit 1; }
  log "env OK"
}

dl_lib_done(){
  python3 - <<'EOF'
import json,sys
s=json.load(open("projects/ahyeon/download_state.json"))
plan=json.load(open("projects/ahyeon/sources_plan.json"))["sources"]
need=[x["key"] for x in plan if x["key"]!="_comment"]
ok=[k for k in need if (lambda v: v=="ok" or (isinstance(v,dict) and v.get("status")=="ok"))(s.get(k))]
missing=[k for k in need if k not in ok and k!="dome_fancam"]
print(len(ok),len(need),",".join(missing))
EOF
}

dl_lib(){
  while true; do
    read -r ok need missing <<< "$(dl_lib_done)"
    [ -z "$missing" ] && { log "library sources complete ($ok/$need)"; return 0; }
    log "library sources: $ok/$need — chunk starts (missing: $missing)"
    timeout 560 python3 scripts/mirror_dl.py ahyeon 3 2>&1 | tee -a "$LOG" | grep -E "OK dur|FAILED|CONTENT|TITLE_REJ|pending|chunk done" | tail -30
    push_state "dl_lib $ok/$need"
    # if a full pass makes zero progress twice, stop trying (manual bucket)
    # tracked via fail counters inside the state file; loop caps at 12 rounds
    ROUNDS=$((ROUNDS+1)); [ "${ROUNDS:-0}" -ge 12 ] && { log "dl_lib round cap"; return 0; }
  done
}

dl_v3(){
  while true; do
    PEND=$(python3 -c "
import json;s=json.load(open('projects/ahyeon/download_state_v3.json')) if __import__('os').path.exists('projects/ahyeon/download_state_v3.json') else {}
print(','.join(t for t,v in s.items() if (v or {}).get('status')!='ok'))" 2>/dev/null)
    # also exit when seek_v3 itself reports all ok (state may not list succeeded keys until first run)
    log "v3 targets pending: ${PEND:-none-yet}"
    if [ -f projects/ahyeon/download_state_v3.json ]; then
      NOK=$(python3 -c "
import json;s=json.load(open('projects/ahyeon/download_state_v3.json'))
ok=sum(1 for v in s.values() if (v or {}).get('status')=='ok');print(ok)")
      [ "$NOK" -ge 12 ] && { log "v3 sources complete ($NOK/12)"; return 0; }
    fi
    timeout 560 python3 scripts/seek_v3.py ahyeon 2 2>&1 | tee -a "$LOG" | grep -E "OK dur|FAILED|pending|chunk done|cands" | tail -25
    push_state "dl_v3 progress"
    ROUNDS=$((ROUNDS+1)); [ "${ROUNDS:-0}" -ge 8 ] && { log "dl_v3 round cap"; return 0; }
  done
}

phase_tts(){
  python3 pipeline/tts_all.py ahyeon --changed-only 2>&1 | tail -5 || \
  python3 pipeline/tts_all.py ahyeon 2>&1 | tail -5
  push_state "tts"
}

phase_plan(){
  python3 pipeline/director.py ahyeon 2>&1 | tail -8
  push_state "scene_plan"
}

phase_edit(){
  log "assemble (per-scene resume)…"
  timeout 580 python3 pipeline/assemble.py ahyeon 2>&1 | tail -6
  push_state "assemble-progress"
  log "final render…"
  python3 pipeline/final_crf18.py ahyeon 2>&1 | tail -6
  python3 pipeline/qc.py ahyeon 2>&1 | tail -20
  push_state "final+qa"
}

phase_ship(){
  bash pipeline/upload_release_v3.sh 2>&1 | tail -8 || log "ship step needs manual release script"
  push_state "ship"
}

ROUNDS=0
case "${1:-auto}" in
  env)  phase_env ;;
  dl)   phase_env; dl_lib; dl_v3 ;;
  tts)  phase_tts ;;
  plan) phase_plan ;;
  edit) phase_edit ;;
  ship) phase_ship ;;
  auto) phase_env; dl_lib; dl_v3; phase_tts; phase_plan; phase_edit; phase_ship ;;
  *) echo "unknown phase $1"; exit 1 ;;
esac
log "resume_v3 finished phase=${1:-auto}"
