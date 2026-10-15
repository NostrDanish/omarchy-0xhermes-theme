#!/usr/bin/env bash
set -euo pipefail

PROFILE="saved-0xhermes"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME:?HOME must be set}/.config/omarchy/branding/screensavers/$PROFILE"

for file in hermes-crazy.mp4 quit-on-key.lua runner.sh 05-0xprivacy-hermes-attract.png README.md; do
  if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
    printf 'Missing package file: %s\n' "$SCRIPT_DIR/$file" >&2
    exit 1
  fi
done

install -d "$DEST"
install -m 0644 "$SCRIPT_DIR/hermes-crazy.mp4" "$DEST/hermes-crazy.mp4"
install -m 0644 "$SCRIPT_DIR/quit-on-key.lua" "$DEST/quit-on-key.lua"
install -m 0644 "$SCRIPT_DIR/05-0xprivacy-hermes-attract.png" "$DEST/05-0xprivacy-hermes-attract.png"
install -m 0644 "$SCRIPT_DIR/README.md" "$DEST/README.md"
install -m 0755 "$SCRIPT_DIR/runner.sh" "$DEST/runner.sh"

printf 'Installed the 0xHermes screensaver profile to %s\n' "$DEST"
printf 'It was not activated. To activate it: omarchy-screensaver-profile set %s\n' "$PROFILE"
