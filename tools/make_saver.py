#!/usr/bin/env python3
"""0xHermes screensaver — animate the APPROVED pixels, never re-derive them.

Why this exists: the v4 loop re-halftoned the girl from the hero's own
luminance (a photocopy of a photocopy), added a bloom whose alpha multiplier
clamped to solid halos, and drew a scan band straight into RGB so its alpha
was discarded and it read as an opaque bar over her eyes. It died.

This loop never touches the portrait. The base frame is the approved plate
(`backgrounds/30-hero-lockup.png`), whose girl pixels are byte-identical to the
loved hero. Motion happens only around her:

  * binary rain in the left/right margins, the way the loved attract loop does it
  * a thin CRT refresh sweep down the frame plus a fainter retrace up it
  * the rose rule under the wordmark breathing in opacity

Every motion is a function of phase p = i/144 with wrap-periodic offsets, so
frame 144 is frame 0 by construction. 12 FPS is the chassis cap (the old 30 FPS
paint cooked a core).

    python3 tools/make_saver.py    # -> screensaver/hermes-rain.mp4 + mark.png
"""
from __future__ import annotations

import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "backgrounds" / "30-hero-lockup.png"
OUT = ROOT / "screensaver" / "hermes-rain.mp4"
POSTER = ROOT / "screensaver" / "mark.png"
PREVIEW = ROOT / "screensaver" / "preview.png"

W, H = 2560, 1080
FRAMES, FPS = 144, 12
PHOSPHOR = (57, 255, 20)
MINT = (131, 255, 96)
ROSE = (255, 46, 99)
FONT_PATH = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"

# margin rain columns: x, tile period in px (also the scroll distance per loop)
COLUMNS = [(10, 216), (30, 180), (W - 44, 252), (W - 24, 198)]
DIGIT_H = 18
RULE_BOX = (1403, 547, 1927, 549)


def rain_tile(period: int, seed: int) -> Image.Image:
    rnd = random.Random(seed)
    rows = period // DIGIT_H
    tile = Image.new("RGBA", (16, period), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    face = ImageFont.truetype(FONT_PATH, 13)
    for i in range(rows):
        d.text((2, i * DIGIT_H), rnd.choice("01"), font=face,
               fill=PHOSPHOR + (135,))
    return tile


def build_base() -> Image.Image:
    return Image.open(BASE).convert("RGBA")


def frame(base: Image.Image, tiles, i: int) -> Image.Image:
    p = i / FRAMES
    im = base.copy()

    for (x, period), tile in zip(COLUMNS, tiles):
        dy = round(p * period)          # wraps exactly: dy(1.0) == period == dy(0)
        im.alpha_composite(tile, (x, -dy))
        im.alpha_composite(tile, (x, -dy + period))

    # CRT refresh sweep down, faint retrace up
    sweep = Image.new("RGBA", (W, 2), MINT + (72,))
    im.alpha_composite(sweep, (0, round(-6 + p * (H + 12))))
    retrace = Image.new("RGBA", (W, 1), MINT + (34,))
    im.alpha_composite(retrace, (0, round(H + 6 - p * (H + 12))))

    # the rose rule breathes
    pulse = Image.new("RGBA", (W, 2), ROSE + (0,))
    a = round(30 + 22 * math.sin(math.tau * p))
    pulse.putalpha(Image.new("L", (W, 2), a))
    im.alpha_composite(pulse, (RULE_BOX[0], RULE_BOX[1]))

    return im.convert("RGB")


def main() -> int:
    base = build_base()
    tiles = [rain_tile(period, seed) for seed, (_, period) in enumerate(COLUMNS, 7)]

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
           "-pix_fmt", "yuv420p", "-g", "24", "-movflags", "+faststart",
           "-metadata", "title=0xHermes - approved pixels, rain and sweep",
           str(OUT)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(FRAMES):
            img = frame(base, tiles, i)
            if i == 0:
                img.save(POSTER, optimize=True)
                img.save(PREVIEW, optimize=True)
            proc.stdin.write(img.tobytes())
    except BrokenPipeError:
        pass
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KiB) + mark.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())