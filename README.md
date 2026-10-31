# 0xHermes — Omarchy theme

Signal-intelligence desktop: forest-black plates, phosphor geometry, one rose
accent for anything that matters. Theme slug: `0xhermes`.

Palette: ink `#020804` · phosphor `#39ff14` · mint `#83ff60` · rose `#ff2e63` ·
depth `#197d43` · foreground `#c7f5ce`.

## What v3 is

- **Four 5120×2160 wallpapers** drawn from one generator: a full-bleed horizon,
  an instrument trace spanning the width, a winged-H sigil in a hexagonal
  aperture, and a type block held inside the safe zone of the top bar.
- **A seamless 12 FPS saver loop** (2560×1080, 144 frames) rendered by the same
  drawing code, so the screensaver and the wallpaper cannot drift apart.
- **A real Hermes skin**: `hermes.yaml` publishes the palette into the Hermes
  desktop app, TUI and CLI.
- **Lock art** with the lower third left clean for the greeter's password field.

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

| File | Picker name | Character |
|---|---|---|
| `00-signal-temple.png` | Signal Temple | hero: sigil, horizon, waveform, full type block |
| `01-open-channel.png` | Open Channel | same plate, quiet: sigil only, one small label |
| `02-ghost-grid.png` | Ghost Grid | no sigil: grid, watermark mark, corner telemetry |
| `03-rose-protocol.png` | Rose Protocol | rose-led accent, rose ring on the sigil |
| `0xhermes.png` | — | byte-identical copy of the hero (picker anchor) |

`preview.png` (2560×1440) and `unlock.png`/`preview-unlock.png` (1024²) are
generated alongside.

## Screensaver

`screensaver/hermes-signal.mp4`: the sigil rotates once per loop, three packet
dots ride closed orbits, a rose scanner sweeps from off-screen left to
off-screen right, and the core light breathes. Nothing is cropped at the loop
point, so `--loop-file=inf` looks continuous.

`omarchy-launch-screensaver force` previews it; any key or click exits. Without
mpv, `mark.py` shows the poster and polls stdin instead of animating.

Details and the file map: `screensaver/README.md`.

## Rebuild

```bash
python3 tools/generate_v3_assets.py           # wallpapers, lock art, previews
python3 tools/generate_v3_assets.py --video   # + the saver loop (ffmpeg/libx264)
python3 tools/generate_v3_assets.py --all     # both
```

Everything is drawn with Pillow: ~35 s for the stills, ~2 min for the loop on
this desktop. No network access at build time, no third-party artwork.

Fonts: JetBrains Mono Nerd Font (`/usr/share/fonts/TTF`), with DejaVu Sans Mono
as the fallback.

## Notes

- `hermes.yaml` must stay pure ASCII — `omarchy-theme-set-hermes` rejects the
  skin if any byte falls outside printable ASCII (an em dash is enough), and the
  failure is only a warning.
- App icons regenerate with `python3 generate-app-icons.py`; Telegram and VS Code
  variants have their own `generate-*.py` scripts.
- `legacy/v1*` and `legacy/v2-second-pass/` hold earlier passes for rollback.
