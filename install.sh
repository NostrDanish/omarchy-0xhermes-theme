#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ICON_SRC="$ROOT/icons/0xPrivacy-Phosphor"
ICON_DEST="${XDG_DATA_HOME:-$HOME/.local/share}/icons/0xPrivacy-Phosphor"

if [[ ! -d "$ICON_SRC" || ! -f "$ROOT/backgrounds/0xhermes.png" ]]; then
  printf 'Theme pack is incomplete.\n' >&2
  exit 1
fi

rm -rf "$ICON_DEST"
mkdir -p "$(dirname "$ICON_DEST")"
cp -a "$ICON_SRC" "$ICON_DEST"
rm -f "$ICON_DEST/icon-theme.cache"
if command -v gtk-update-icon-cache >/dev/null; then
  gtk-update-icon-cache -f "$ICON_DEST" >/dev/null
fi

bash "$ROOT/screensaver/install.sh"

printf '0xhermes pieces installed (icons + screensaver override).\n'
printf 'Select the theme with: omarchy theme set 0xhermes\n'
printf 'Preview the saver:     omarchy-launch-screensaver force\n'
