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

## Asset catalog

**Favorites** — the approved set. 2560×1080 unless noted.

| File | Size | Source | What it is |
|---|---|---|---|
| `backgrounds/0xhermes.png` | 2560×1080 | original | the hero: girl + `0x PRIVACY` lockup (picker anchor) |
| `backgrounds/00-with-logo.png` | 2560×1080 | original | byte-identical to `0xhermes.png` |
| `backgrounds/01-no-logo.png` | 2560×1080 | original | hero, girl only |
| `backgrounds/02-wordmark.png` | 2560×1080 | original | wordmark plate |
| `backgrounds/03-cipher-storm.png` | 2560×1080 | original | `TRUST NOTHING · VERIFY EVERYTHING` variant |
| `backgrounds/30-hero-lockup.png` | 2560×1080 | `tools/make_plate.py` | hero with the rule flushed under the wordmark |
| `screensaver/hermes-rain.mp4` | 2560×1080, 12 fps, 12 s | `tools/make_saver.py` | **lead loop** — the plate with margin rain, CRT sweep, breathing rule |
| `screensaver/hermes-crazy.mp4` | 1920×1080, 12 fps, 6 s | original | loved fallback (upscaled on this panel) |
| `screensaver/mark.png` | 2560×1080 | `tools/make_saver.py` | poster — frame 0 of the rain loop |

**Alternates** — kept and installed as fallbacks, not the approved look.

| File | Size | What it is |
|---|---|---|
| `screensaver/hermes-signal.mp4` | 2560×1080, 12 fps, 12 s | v3 signal-temple loop, third fallback |
| `backgrounds/10-signal-temple.png` | 2560×1080 | v3 signal-temple plate |
| `backgrounds/11`–`13-*.png` | 2560×1080 | the rest of the v3 plates |

**Derived branding** — regenerated from the plate, never hand-edited.

| File | Size | What it is |
|---|---|---|
| `preview.png` | 2560×1440 | picker preview: the plate 1:1, ink-padded (never upscaled) |
| `unlock.png`, `preview-unlock.png` | 1024×1024 | lock surface: the girl 1:1, centred on ink |
| `screensaver/preview.png` | 2560×1080 | poster copy (frame 0) |

**Quarantined** — tracked, so the lineage stays recoverable, never installed.

| File | What it is |
|---|---|
| `legacy/v4-rejected/` | the rejected v4 dot-matrix build: plates, loop, generator |
| `legacy/v3-signal-temple/preview-emblem.png` | the v3 emblem that `screensaver/preview.png` used to be |

Photo-derived wallpapers, `cage.mp4` and `screensaver/plates/` are excluded on
purpose — they are not the approved art and are not installed.

## Screensaver

`screensaver/hermes-rain.mp4`: the lead loop — the approved plate with motion
only *around* the girl: binary rain in the margins, a 2 px CRT refresh sweep, and
the rose rule under the wordmark breathing. 2560×1080, 12 FPS, 12 seconds,
H.264, no audio. Her pixels are never re-rendered, and every motion is periodic
over 144 frames, so frame 144 is frame 0 by construction.

`screensaver/hermes-crazy.mp4`: the loved original attract loop — 1920×1080, so
it is upscaled onto a 2560×1080 panel and her scanlines soften. Kept as the
first fallback. `hermes-signal.mp4` (the v3 signal loop) is the second.

`omarchy-launch-screensaver force` previews it; any key or click exits. Without
mpv, `mark.py` shows the poster and polls stdin instead of animating.

Details and the file map: `screensaver/README.md`.

## Rebuild

```bash
python3 tools/make_plate.py              # 30-hero-lockup.png + preview/unlock art
python3 tools/make_saver.py              # hermes-rain.mp4 + mark.png + preview.png
```

`make_plate.py` pastes the girl's real pixels out of `backgrounds/0xhermes.png`
at 1:1 and only fixes the rule under the wordmark, so the plate can only be as
sharp as the hero — there is no higher-resolution source. `make_saver.py` uses
that plate as its base frame and moves rain, sweep and rule *around* her; it
never re-renders her. Fonts: JetBrains Mono Nerd Font (`/usr/share/fonts/TTF`),
DejaVu Sans Mono as the fallback.

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