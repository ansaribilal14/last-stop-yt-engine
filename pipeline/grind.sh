#!/bin/bash
# grind.sh — download queue driver (R8: local-only, no Actions).
# Egress: direct first, then validated proxies from /tmp/good_proxies.json.
# Recipe: yt-dlp master + yt-dlp-ejs (local solver) + bgutil POT @4416
#         + client ladder tv_simply -> mweb,web_safari -> web
export PATH="$HOME/.local/bin:$PATH"
CACHE=/home/z/my-project/engine/projects/blackpink/ytdl_cache
YTDLP="python3 -m yt_dlp"
mkdir -p "$CACHE"

queue() { # ids of wave not yet on disk (>1MB)
  python3 - "$1" << 'PYEOF'
import json,os,sys
WAVES=json.load(open('/home/z/my-project/engine/pipeline/waves.json'))
CACHE='/home/z/my-project/engine/projects/blackpink/ytdl_cache'
for v in WAVES[sys.argv[1]]:
    if not (os.path.exists(f'{CACHE}/{v}.mp4') and os.path.getsize(f'{CACHE}/{v}.mp4')>1_000_000):
        print(v)
PYEOF
}

try_one() {
  local VID="$1"
  local URL="https://www.youtube.com/watch?v=$VID"
  local PROXIES=("" $(python3 -c "
import json,os
try: print(' '.join(p['url'] for p in json.load(open('/tmp/good_proxies.json'))[:12]))
except Exception: pass"))
  for PX in "${PROXIES[@]}"; do
    local PARG=(); [ -n "$PX" ] && PARG=(--proxy "$PX")
    for CLIENT in "tv_simply" "mweb,web_safari" "web"; do
      timeout 150 $YTDLP --no-cache-dir --no-check-certificates --js-runtimes node \
        -N 4 --retries 2 --no-part "${PARG[@]}" \
        --extractor-args "youtube:player_client=$CLIENT" \
        --extractor-args "youtubepot-bgutilhttp:base_url=http://127.0.0.1:4416" \
        -f "bv*[vcodec^=avc1][height<=720]+ba[height<=720][ext=mp4]/b" \
        -S "res:720,vcodec:avc" --merge-output-format mp4 \
        -o "$CACHE/$VID.%(ext)s" "$URL" > "$CACHE/lad_$VID.log" 2>&1
      if [ -s "$CACHE/$VID.mp4" ] && [ "$(stat -c%s "$CACHE/$VID.mp4" 2>/dev/null || echo 0)" -gt 1000000 ]; then
        echo "OK $VID via ${CLIENT} $( [ -n "$PX" ] && echo proxy || echo direct)"
        return 0
      fi
    done
  done
  echo "FAIL $VID: $(grep -o 'ERROR:.*' "$CACHE/lad_$VID.log" | head -1 | cut -c1-100)"
  return 1
}

WAVE="${1:-all}"
if [ "$WAVE" = "all" ]; then
  for W in mv1 live solos1 solos2 interviews context; do
    for V in $(queue $W); do try_one "$V"; done
  done
else
  for V in $(queue $WAVE); do try_one "$V"; done
fi
echo "GRIND DONE: $(ls $CACHE/*.mp4 2>/dev/null | wc -l) videos cached"
