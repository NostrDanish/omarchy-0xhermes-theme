# 0xHermes — Omarchy theme

Signal-intelligence desktop: forest-black plates, phosphor geometry, one rose
accent for anything that matters. Theme slug: `0xhermes`.

Palette: ink `#020804` · phosphor `#39ff14` · mint `#83ff60` · rose `#ff2e63` ·
depth `#197d43` · foreground `#c7f5ce`.

## What this theme is

The portrait is **not redrawn**. `backgrounds/0xhermes.png` and the 00–03 set
are the original 2560×1080 artwork — the girl's real pixels, the approved
letterforms — and they are byte-identical to what shipped. 2560×1080 is
native to this panel, so they land 1:1.

`backgrounds/30-hero-lockup.png` is the one plate built on top of them
(`tools/make_plate.py`): same girl, same wordmark, same tagline, every ink
pixel byte-identical — the only change is the rule under `0x PRIVACY`, which
used to stop 82 px short of PRIVACY's last stem and now runs flush from the
wordmark's left edge to it, tying `0x` and `PRIVACY` into one lockup.

A previous pass rebuilt the girl by recovering her luminance from the hero's
own pixels and re-halftoning it onto a new dot grid, then added a Gaussian
bloom and a scan band. That was a photocopy of a photocopy and it looked
worse than the original; its plates and loop live in `legacy/v4-rejected/`.

## Install

```bash
mkdir -p ~/.config/omarchy/themes
ln -sfn ~/Work/omarchy-0xhermes-theme ~/.config/omarchy/themes/0xhermes
bash ~/.config/omarchy/themes/0xhermes/install.sh
omarchy theme refresh
omarchy theme bg next
```

`install.sh` checks the assets, installs the saver profile, drops the launcher
into `~/.local/bin`, and wires the local-bin preference the idle timer uses. It
never changes your idle timeout.

## Wallpapers

| File | Character |
|---|---|
| `0xhermes.png` | the hero: girl + `0x PRIVACY` lockup (picker anchor) |
| `00-with-logo.png` | hero with the logo |
| `01-no-logo.png` | hero, girl only |
| `02-wordmark.png` | wordmark plate |
| `03-cipher-storm.png` | `TRUST NOTHING · VERIFY EVERYTHING` variant |
| `30-hero-lockup.png` | hero with the rule fixed under the wordmark |
| `10`–`13-*.png` | the v3 signal-temple plates (kept as alternates) |

`preview.png` (2560×1440) and `unlock.png`/`preview-unlock.png` (1024²) are
generated alongside.

## Screensaver

`screensaver/hermes-crazy.mp4`: the loved attract loop — 2560×1080, 12 FPS,
12 seconds, H.264, no audio. It is the lead clip; `hermes-signal.mp4` (the v3
signal loop) is the fallback.

`omarchy-launch-screensaver force` previews it; any key or click exits. Without
mpv, `mark.py` shows the poster and polls stdin instead of animating.

Details and the file map: `screensaver/README.md`.

## Rebuild

```bash
python3 tools/make_plate.py              # backgrounds/30-hero-lockup.png
```

The plate is built from the hero's own pixels with Pillow, so it can only be
as sharp as the hero — there is no higher-resolution source. Fonts:
JetBrains Mono Nerd Font (`/usr/share/fonts/TTF`), DejaVu Sans Mono as the
fallback.

## Notes

- `hermes.yaml` must stay pure ASCII — `omarchy-theme-set-hermes` rejects the
  skin if any byte falls outside printable ASCII (an em dash is enough), and the
  failure is only a warning.
- `hyprland.lua` borders apply at the next Hyprland start; `hyprctl reload`
  does not re-read the Lua config.
- App icons regenerate with `python3 generate-app-icons.py`; Telegram and VS Code
  variants have their own `generate-*.py` scripts.
- `legacy/v1*`, `legacy/v2-second-pass/`, `legacy/v3-signal-temple/` and
  `legacy/v4-rejected/` hold earlier passes for rollback.