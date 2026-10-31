#!/usr/bin/env bash
set -euo pipefail

# Install/update the 0xHermes V3 theme assets, icons, and screensaver profile.
PROFILE="saved-0xhermes"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME:?HOME must be set}/.config/omarchy/branding/screensavers/$PROFILE"
BIN_DEST="${HOME}/.local/bin/omarchy-screensaver"
HYPR_DIR="${HOME}/.config/hypr"
HYPR_PATH_LUA="$HYPR_DIR/prefer-local-bin.lua"
HYPRLAND_LUA="$HYPR_DIR/hyprland.lua"

# Required assets: wallpapers, saver loop, poster, launcher
for file in \
  colors.toml \
  backgrounds/0xhermes.png \
  backgrounds/00-with-logo.png \
  backgrounds/01-no-logo.png \
  backgrounds/02-wordmark.png \
  backgrounds/03-cipher-storm.png \
  backgrounds/10-signal-temple.png \
  backgrounds/30-hero-lockup.png \
  preview.png \
  unlock.png \
  screensaver/hermes-rain.mp4 \
  screensaver/hermes-crazy.mp4 \
  screensaver/hermes-signal.mp4 \
  screensaver/mark.png \
  screensaver/runner.sh \
  screensaver/mark.py \
  screensaver/omarchy-screensaver \
  README.md; do
  if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
    printf 'Missing: %s\n' "$SCRIPT_DIR/$file" >&2
    exit 1
  fi
done

# Preserve user icons: merge theme assets
ICON_SRC="$SCRIPT_DIR/icons/0xPrivacy-Phosphor"
ICON_DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons/0xPrivacy-Phosphor"
if [[ -d "$ICON_SRC" ]]; then
  mkdir -p "$ICON_DEST"
  cp -a "$ICON_SRC/." "$ICON_DEST/"
  rm -f "$ICON_DEST/icon-theme.cache"
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f "$ICON_DEST" >/dev/null 2>&1 || true
  fi
fi

# Install the saver profile: loop, poster, launcher scripts
install -d "$DEST"
install -m 0644 "$SCRIPT_DIR/screensaver/hermes-rain.mp4" "$DEST/hermes-rain.mp4"
install -m 0644 "$SCRIPT_DIR/screensaver/hermes-crazy.mp4" "$DEST/hermes-crazy.mp4"
install -m 0644 "$SCRIPT_DIR/screensaver/hermes-signal.mp4" "$DEST/hermes-signal.mp4"
install -m 0644 "$SCRIPT_DIR/screensaver/quit-on-key.lua" "$DEST/quit-on-key.lua"
install -m 0644 "$SCRIPT_DIR/screensaver/mark.py" "$DEST/mark.py"
install -m 0644 "$SCRIPT_DIR/screensaver/mark.png" "$DEST/mark.png"
install -m 0644 "$SCRIPT_DIR/screensaver/mark.png" "$DEST/preview.png"
install -m 0644 "$SCRIPT_DIR/screensaver/README.md" "$DEST/README.md"
install -m 0755 "$SCRIPT_DIR/screensaver/runner.sh" "$DEST/runner.sh"
# v2 leftovers are no longer referenced by any path
rm -f "$DEST/hermes-v2.mp4" "$DEST/v3-signal.html" "$DEST/hermes-dots.mp4"

# Install screensaver wrapper to ~/.local/bin
install -d "$(dirname "$BIN_DEST")"
install -m 0755 "$SCRIPT_DIR/screensaver/omarchy-screensaver" "$BIN_DEST"

# Install Hyprland path preference
install -d "$HYPR_DIR"
# Prefer the local 0xHermes saver when Omarchy's idle timer fires
install -m 0644 "$SCRIPT_DIR/screensaver/prefer-local-bin.lua" "$HYPR_PATH_LUA"

# Add prefer-local-bin require to Hyprland config
if [[ -f $HYPRLAND_LUA ]] && ! grep -q 'prefer-local-bin' "$HYPRLAND_LUA" 2>/dev/null; then
  if grep -q 'require("hypr.autostart")' "$HYPRLAND_LUA"; then
    sed -i '/require("hypr.autostart")/a\
\
-- 0xHermes: prefer ~/.local/bin for theme savers\
require("hypr.prefer-local-bin")
' "$HYPRLAND_LUA"
  else
    printf '\n-- 0xHermes V3: prefer local bin for interactive saver\nrequire("hypr.prefer-local-bin")\n' >>"$HYPRLAND_LUA"
  fi
fi

printf '0xHermes v3 installed.\n'
printf 'Theme dir:  %s\n' "$SCRIPT_DIR"
printf 'Saver:      hermes-crazy.mp4 (loved loop) with hermes-signal.mp4 fallback\n'
printf 'Profile:    %s\n' "$DEST"
printf 'Preview:    omarchy-launch-screensaver force\n'
printf 'Wallpaper:  omarchy theme bg next   (or: omarchy theme bg set "Signal Temple")\n'