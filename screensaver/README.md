# 0xHermes screensaver

The loved attract loop: 2560×1080, 12 FPS, 12 seconds, H.264, no audio.
It is pre-rendered, so the idle path does no per-pixel animation work.

`runner.sh` prefers mpv with safe hardware decoding and low process priority; if
mpv is missing or fails, `mark.py` falls back to the poster frame with
lightweight input polling instead of a repaint loop.

## Files

| File | Role |
|---|---|
| `hermes-crazy.mp4` | the loved attract loop (lead) |
| `hermes-signal.mp4` | the v3 signal-temple loop (fallback) |
| `mark.png` | poster frame, also the fallback image |
| `mark.py` | no-mpv fallback: draws the poster, polls stdin, exits on a key |
| `runner.sh` | picks mpv or the fallback, sets a near-black terminal background |
| `quit-on-key.lua` | mpv script: any key or click quits |
| `omarchy-screensaver` | entry point Omarchy's idle launcher calls |
| `prefer-local-bin.lua` | puts `~/.local/bin` ahead of the stock saver |

## Install

```bash
bash ~/.config/omarchy/themes/0xhermes/screensaver/install.sh
```

This updates `~/.local/bin/omarchy-screensaver`, the `saved-0xhermes` snapshot,
and the Hyprland local-bin preference used by Omarchy's idle launcher. It does
not change the idle timeout.

Preview: `omarchy-launch-screensaver force`
Stock fallback: `/usr/share/omarchy/bin/omarchy-screensaver`

Any key or click exits. Do not pass `--fps` to mpv; the file is already encoded
at 12 FPS.

## Rebuild

The clips are encoded from Pillow frames with ffmpeg/libx264 (yuv420p, CRF 18),
so the saver and the desktop art share one palette. A rejected v4 loop — dots
re-halftoned from the hero's own luminance, with a bloom that clamped to solid
halos and a scan band drawn without alpha compositing — is kept in
`legacy/v4-rejected/` for rollback only.