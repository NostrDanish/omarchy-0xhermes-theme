# 0xHermes

Omarchy theme. Install name is `0xhermes`, the same shape as `0xprivacy` and `dedsec`.

Forest black, neon `#39ff14`, rose `#ff2e63`. Four wallpaper logos, the green/red icon set, and a 12 FPS screensaver of the with-logo still.

## Install

A bare `omarchy theme install` clone is untrusted: Omarchy drops `hyprland.lua`, `neovim.lua`, terminal configs, and `vscode.json`. Use a symlink to your own checkout so the full theme applies, then run the installer for icons and the screensaver override.

```bash
git clone https://github.com/NostrDanish/omarchy-0xhermes-theme ~/Work/omarchy-0xhermes-theme
mkdir -p ~/.config/omarchy/themes
ln -sfn ~/Work/omarchy-0xhermes-theme ~/.config/omarchy/themes/0xhermes
bash ~/.config/omarchy/themes/0xhermes/install.sh
omarchy theme set 0xhermes
```

Theme directory name must be `0xhermes`. Do not pass `0xHermes`.

`install.sh` copies the Phosphor icons and installs `~/.local/bin/omarchy-screensaver` so idle uses the 0xHermes mpv loop. Stock ttfx remains at `/usr/share/omarchy/bin/omarchy-screensaver`.

## Wallpapers

The background picker labels come from the filenames. `omarchy theme bg next` walks them in this order.

| File | Picker label | What it is |
|---|---|---|
| `backgrounds/00-with-logo.png` | 00 With Logo | Mascot plus the `0x PRIVACY` wordmark. Default. Same bytes as `0xhermes.png`. |
| `backgrounds/01-no-logo.png` | 01 No Logo | Mascot only. No wordmark. |
| `backgrounds/02-wordmark.png` | 02 Wordmark | `0x PRIVACY` text. No mascot. |
| `backgrounds/03-cipher-storm.png` | 03 Cipher Storm | Mascot, wordmark, and the verify line. |

`backgrounds/0xhermes.png` is the frozen with-logo still. Do not regenerate or delete it. It is the same image as `00-with-logo.png`, so the picker lists both.

## Screensaver

`install.sh` installs `~/.local/bin/omarchy-screensaver` so idle uses the 0xHermes loop. Stock ttfx stays at `/usr/share/omarchy/bin/omarchy-screensaver`.

Preview: `omarchy-launch-screensaver force`

The loop is `screensaver/hermes-crazy.mp4`: the with-logo wallpaper, rose scan, phosphor shear, margin rain. Six seconds, 12 FPS. Any ordinary key quits. Do not pass `--fps` to mpv.
