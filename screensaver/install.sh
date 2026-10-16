#!/usr/bin/env bash
set -euo pipefail

# Wire the 0xHermes saver for current Omarchy:
# 1. ~/.local/bin/omarchy-screensaver shadows the stock ttfx binary
# 2. Hyprland must put ~/.local/bin before $OMARCHY_PATH/bin (Omarchy
#    prepends its bin in envs.lua, which otherwise wins for idle launches)
# There is no omarchy-screensaver-profile command on current Omarchy.

PROFILE="saved-0xhermes"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME:?HOME must be set}/.config/omarchy/branding/screensavers/$PROFILE"
BIN_DEST="${HOME}/.local/bin/omarchy-screensaver"
HYPR_DIR="${HOME}/.config/hypr"
HYPR_PATH_LUA="$HYPR_DIR/prefer-local-bin.lua"
HYPRLAND_LUA="$HYPR_DIR/hyprland.lua"

for file in hermes-crazy.mp4 quit-on-key.lua runner.sh mark.py mark.png \
  05-0xprivacy-hermes-attract.png README.md omarchy-screensaver prefer-local-bin.lua; do
  if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
    printf 'Missing package file: %s\n' "$SCRIPT_DIR/$file" >&2
    exit 1
  fi
done

install -d "$DEST"
install -m 0644 "$SCRIPT_DIR/hermes-crazy.mp4" "$DEST/hermes-crazy.mp4"
install -m 0644 "$SCRIPT_DIR/quit-on-key.lua" "$DEST/quit-on-key.lua"
install -m 0644 "$SCRIPT_DIR/mark.py" "$DEST/mark.py"
install -m 0644 "$SCRIPT_DIR/mark.png" "$DEST/mark.png"
install -m 0644 "$SCRIPT_DIR/05-0xprivacy-hermes-attract.png" "$DEST/05-0xprivacy-hermes-attract.png"
install -m 0644 "$SCRIPT_DIR/README.md" "$DEST/README.md"
install -m 0755 "$SCRIPT_DIR/runner.sh" "$DEST/runner.sh"

install -d "$(dirname "$BIN_DEST")"
install -m 0755 "$SCRIPT_DIR/omarchy-screensaver" "$BIN_DEST"

install -d "$HYPR_DIR"
install -m 0644 "$SCRIPT_DIR/prefer-local-bin.lua" "$HYPR_PATH_LUA"

if [[ -f $HYPRLAND_LUA ]] && ! grep -q 'prefer-local-bin' "$HYPRLAND_LUA"; then
  if grep -q 'require("hypr.autostart")' "$HYPRLAND_LUA"; then
    # shellcheck disable=SC2016
    sed -i '/require("hypr.autostart")/a\
\
-- After Omarchy prepends $OMARCHY_PATH/bin, put ~/.local/bin first again so\
-- theme screensavers (0xhermes) override the stock ttfx saver.\
require("hypr.prefer-local-bin")
' "$HYPRLAND_LUA"
  else
    printf '\nrequire("hypr.prefer-local-bin")\n' >>"$HYPRLAND_LUA"
  fi
fi

printf 'Installed the 0xHermes screensaver.\n'
printf 'Active launcher: %s\n' "$BIN_DEST"
printf 'Hyprland PATH:   %s\n' "$HYPR_PATH_LUA"
printf 'Profile copy:    %s\n' "$DEST"
printf 'Preview:         omarchy-launch-screensaver force\n'
printf 'Stock fallback:  /usr/share/omarchy/bin/omarchy-screensaver\n'
printf 'Reload Hyprland if the saver still shows stock ASCII: hyprctl reload\n'
