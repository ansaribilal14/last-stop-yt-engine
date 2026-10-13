#!/bin/bash
# grind.sh — download queue driver (R8: local-only, no Actions).
# Usage: grind.sh [wave|all] [project]
# Egress: validated proxies from /tmp/good_proxies.json (rotating), then direct.
# Recipe: yt-dlp + bgutil POT @4416 (auto-started here)
#         + client ladder tv_simply -> mweb,web_safari -> web
export PATH="$HOME/.local/bin:$PATH"
PROJ="${2:-blackpink}"
CACHE="/home/z/my-project/engine/projects/$PROJ/ytdl_cache"
WAVES="/home/z/my-project/engine/projects/$PROJ/waves.json"
[ -f "$WAVES" ] || WAVES="/home/z/my-project/engine/pipeline/waves.json"
mkdir -p "$CACHE"

# auto-start POT server if not running
if ! curl -s -m 2 http://127.0.0.1:4416/ping > /dev/null 2>&1; then
  (nohup node /home/z/bgutil-ytdlp-pot-provider/server/build/main.js > /tmp/pot.log 2>&1 &)
  sleep 4
fi

queue() {
  python3 - "$1" "$WAVES" "$CACHE" << 'PYEOF'
import json,os,sys
WAVES=json.load(open(sys.argv[2]))
CACHE=sys.argv[3]
for v in WAVES[sys.argv[1]]:
    if not (os.path.exists(f'{CACHE}/{v}.mp4') and os.path.getsize(f'{CACHE}/{v}.mp4')>1_000_000):
        print(v)
PYEOF
}

try_one() {
  local CACHE="$CACHE"
  local VID="$1"
  local URL="https://www.youtube.com/watch?v=$VID"
  local PROXIES=$(python3 -c "
import json
try:
    ps=[p['url'] for p in json.load(open('/tmp/good_proxies.json'))]
    import random; random.shuffle(ps); print(' '.join(ps[:8]))
except Exception: pass")
  for PX in $PROXIES ""; do
    local PARG=(); [ -n "$PX" ] && PARG=(--proxy "$PX")
    for CLIENT in "tv_simply" "mweb,web_safari" "web"; do
      timeout 90 python3 -m yt_dlp --no-cache-dir --no-check-certificates \
        --js-runtimes node -N 4 --retries 1 --no-part "${PARG[@]}" \
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
  echo "FAIL $VID: $(grep -o 'ERROR:.*' "$CACHE/lad_$VID.log" | head -1 | cut -c1-90)"
  return 1
}

WAVE="${1:-all}"
if [ "$WAVE" = "all" ]; then
  Q=""
  for W in mv1 live solos1 solos2 interviews context; do
    Q="$Q $(queue $W 2>/dev/null)"
  done
else
  Q=$(queue $WAVE)
fi
echo "$Q" | tr ' ' '\n' | grep -v '^$' | xargs -P 2 -I{} bash -c "$(declare -f try_one); try_one {}"
echo "GRIND DONE [$PROJ]: $(ls $CACHE/*.mp4 2>/dev/null | wc -l) videos cached"
