#!/usr/bin/env bash
set -euo pipefail

# Install/update the 0xHermes v3 screensaver assets and local PATH override.
PROFILE="saved-0xhermes"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME:?HOME must be set}/.config/omarchy/branding/screensavers/$PROFILE"
BIN_DEST="${HOME}/.local/bin/omarchy-screensaver"
HYPR_DIR="${HOME}/.config/hypr"
HYPR_PATH_LUA="$HYPR_DIR/prefer-local-bin.lua"
HYPRLAND_LUA="$HYPR_DIR/hyprland.lua"

for file in hermes-crazy.mp4 hermes-signal.mp4 quit-on-key.lua runner.sh mark.py mark.png preview.png \
  README.md omarchy-screensaver prefer-local-bin.lua; do
  if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
    printf 'Missing package file: %s\n' "$SCRIPT_DIR/$file" >&2
    exit 1
  fi
done

install -d "$DEST"
install -m 0644 "$SCRIPT_DIR/hermes-crazy.mp4" "$DEST/hermes-crazy.mp4"
install -m 0644 "$SCRIPT_DIR/hermes-signal.mp4" "$DEST/hermes-signal.mp4"
rm -f "$DEST/hermes-v2.mp4"
install -m 0644 "$SCRIPT_DIR/quit-on-key.lua" "$DEST/quit-on-key.lua"
install -m 0644 "$SCRIPT_DIR/mark.py" "$DEST/mark.py"
install -m 0644 "$SCRIPT_DIR/mark.png" "$DEST/mark.png"
install -m 0644 "$SCRIPT_DIR/preview.png" "$DEST/preview.png"
install -m 0644 "$SCRIPT_DIR/README.md" "$DEST/README.md"
install -m 0755 "$SCRIPT_DIR/runner.sh" "$DEST/runner.sh"

install -d "$(dirname "$BIN_DEST")"
install -m 0755 "$SCRIPT_DIR/omarchy-screensaver" "$BIN_DEST"

install -d "$HYPR_DIR"
install -m 0644 "$SCRIPT_DIR/prefer-local-bin.lua" "$HYPR_PATH_LUA"

if [[ -f $HYPRLAND_LUA ]] && ! grep -q 'prefer-local-bin' "$HYPRLAND_LUA" 2>/dev/null; then
  printf '\n-- Prefer the local 0xHermes screensaver over the stock saver.\nrequire("hypr.prefer-local-bin")\n' >>"$HYPRLAND_LUA"
fi

printf 'Installed the 0xHermes v3 screensaver.\n'
printf 'Active launcher: %s\n' "$BIN_DEST"
printf 'Profile copy:    %s\n' "$DEST"
printf 'Loop:            2560x1080, 12 FPS, seamless 12 seconds\n'
printf 'Preview:         omarchy-launch-screensaver force\n'
printf 'Reload Hyprland if idle still uses the stock saver: hyprctl reload\n'