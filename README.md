# 0xHermes

Omarchy theme. Install name is `0xhermes`, the same shape as `0xprivacy` and `dedsec`.

Forest black, neon `#39ff14`, rose `#ff2e63`. Four wallpaper logos, the green/red icon set, and a 12 FPS screensaver of the with-logo still.

## Install

```bash
omarchy theme install https://github.com/NostrDanish/omarchy-0xhermes-theme
bash ~/.config/omarchy/themes/0xhermes/install.sh
omarchy theme set 0xhermes
```

`omarchy theme install` lowercases the repo and strips `omarchy-` and `-theme`, so this repository lands in `~/.config/omarchy/themes/0xhermes`. Do not pass `0xHermes`. That name is not a theme directory.

A git checkout is untrusted. Omarchy then drops `hyprland.lua`, `neovim.lua`, and `vscode.json`. On a machine where those files should apply, replace the checkout with a symlink to your own copy and run `omarchy theme refresh`.

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

`install.sh` copies the profile to `~/.config/omarchy/branding/screensavers/saved-0xhermes`. It does not select it.

```bash
omarchy-screensaver-profile set saved-0xhermes
```

The loop is `screensaver/hermes-crazy.mp4`: the with-logo wallpaper, rose scan, phosphor shear, margin rain. Six seconds, 12 FPS. Any ordinary key quits. Do not pass `--fps` to mpv.
