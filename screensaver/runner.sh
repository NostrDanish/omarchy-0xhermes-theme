#!/usr/bin/env bash
set -euo pipefail

# 0xHermes wallpaper, animated as one 12 FPS loop. Low priority.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VIDEO="$SCRIPT_DIR/hermes-crazy.mp4"
QUIT="$SCRIPT_DIR/quit-on-key.lua"

restore_cursor() {
  hyprctl eval 'hl.config({ cursor = { invisible = false } })' &>/dev/null || true
}
trap restore_cursor EXIT INT TERM HUP QUIT

printf '\033]11;rgb:02/08/04\007'
hyprctl eval 'hl.config({ cursor = { invisible = true } })' &>/dev/null || true

if [[ -f "$VIDEO" && -f "$QUIT" ]] && command -v mpv >/dev/null; then
  nice -n 15 ionice -c3 mpv \
    --fs \
    --ontop \
    --no-border \
    --no-audio \
    --really-quiet \
    --loop-file=inf \
    --hwdec=no \
    --vo=wlshm \
    --profile=fast \
    --osc=no \
    --osd-level=0 \
    --cursor-autohide=always \
    --input-default-bindings=no \
    --input-terminal=no \
    --script="$QUIT" \
    "$VIDEO" && exit 0
fi

export OMARCHY_SAVER_FPS=12
export PYTHONDONTWRITEBYTECODE=1
exec nice -n 15 ionice -c3 /usr/bin/python3 -B -O "$SCRIPT_DIR/mark.py"
