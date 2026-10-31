#!/usr/bin/env bash
set -euo pipefail

# 0xHermes v3: pre-rendered 12 FPS loop, low priority, no audio.
# Without mpv this falls back to mark.py (poster + input poll, no repaint loop).
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VIDEO="$SCRIPT_DIR/hermes-crazy.mp4"
LEGACY_VIDEO="$SCRIPT_DIR/hermes-signal.mp4"
QUIT="$SCRIPT_DIR/quit-on-key.lua"

[[ -f $VIDEO ]] || VIDEO="$LEGACY_VIDEO"

printf '\033]11;rgb:02/08/04\007'

player_pid=""
stop_player() {
  if [[ -n "$player_pid" ]] && kill -0 "$player_pid" 2>/dev/null; then
    kill -TERM "$player_pid" 2>/dev/null || true
    wait "$player_pid" 2>/dev/null || true
  fi
}
handle_signal() {
  stop_player
  exit 0
}
trap handle_signal INT TERM HUP

if [[ -f "$VIDEO" && -f "$QUIT" ]] && command -v mpv >/dev/null 2>&1; then
  nice -n 15 ionice -c3 mpv \
    --fs \
    --panscan=1.0 \
    --ontop \
    --no-border \
    --no-audio \
    --really-quiet \
    --loop-file=inf \
    --hwdec=auto-safe \
    --vo=gpu \
    --profile=fast \
    --osc=no \
    --osd-level=0 \
    --cursor-autohide=always \
    --input-default-bindings=no \
    --input-terminal=no \
    --script="$QUIT" \
    "$VIDEO" &
  player_pid=$!
  if wait "$player_pid"; then
    player_pid=""
    exit 0
  fi
  player_pid=""
fi

# Fallback is intentionally capped and avoids repeatedly repainting the screen.
export OMARCHY_SAVER_FPS="${OMARCHY_SAVER_FPS:-12}"
export PYTHONDONTWRITEBYTECODE=1
exec nice -n 15 ionice -c3 /usr/bin/python3 -B -O "$SCRIPT_DIR/mark.py"
