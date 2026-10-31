# 0xHermes v3 screensaver — Signal Temple

A slow orbital signal loop: 2560×1080, 12 FPS, 12 seconds, H.264, no audio.
It is pre-rendered, so the idle path does no per-pixel animation work.

The loop is seamless by construction: the dashed ring turns exactly once, the
three packet orbits complete whole turns, and the scanner sweep is off-canvas at
both ends. Looping the file therefore has no visible cut.

`runner.sh` prefers mpv with safe hardware decoding and low process priority; if
mpv is missing or fails, `mark.py` falls back to the poster frame with
lightweight input polling instead of a repaint loop.

## Files

| File | Role |
|---|---|
| `hermes-dots.mp4` | the v4 loop: dot dissolve wave, breathing bloom, scan sweep |
| `hermes-crazy.mp4` | the loved original attract loop (first fallback) |
| `hermes-signal.mp4` | the v3 signal-temple loop (second fallback) |
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

```bash
python3 tools/generate_v3_assets.py --video
```

The encoder writes yuv420p H.264 at CRF 18 from the same Pillow drawing code
that makes the wallpapers, so the saver and the desktop art share one palette.
