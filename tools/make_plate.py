#!/usr/bin/env python3
"""0xHermes v4 — build the plate FROM the loved pixels, never re-render them.

Why: the v4 attempt recovered the girl's luminance from the hero's own pixels
and re-halftoned it onto a new dot grid, then added a "bloom" that multiplied
alpha ~61x and a scan band drawn straight into RGB (alpha discarded, so it read
as an opaque bar over her eyes). The originals are 2560x1080 - native to this
panel - and the portrait is horizontal scanline hatching in one flat green.
There is nothing to re-derive, and nothing here can add detail that is not
already in the file.

So this only does what the original got slightly wrong:
  * the rule under PRIVACY stops 82px short of the last stem -> flush it
  * the tagline floats left under "0x" -> align it to the wordmark's left edge
Everything else is the approved pixels, untouched.

    python3 tools/make_plate.py    # -> backgrounds/30-hero-lockup.png

shortcut: the girl is pasted 1:1 from a 2560x1080 source, so the plate is
native to this 2560x1080 panel; a hi-dpi panel needs a new source, not an
upscale of this one.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "backgrounds" / "0xhermes.png"
OUT = ROOT / "backgrounds" / "30-hero-lockup.png"
PREVIEW_OUT = ROOT / "preview.png"
UNLOCK_OUT = ROOT / "unlock.png"
UNLOCK_PREVIEW_OUT = ROOT / "preview-unlock.png"

W, H = 2560, 1080
INK = (2, 8, 4)

# measured out of backgrounds/0xhermes.png
GIRL_BOX = (631, 122, 1400, 940)   # girl art bbox
ROSE_BOX = (1400, 466, 1506, 537)  # rose "0x"
GREEN_BOX = (1525, 466, 1930, 537)  # green "PRIVACY"
TAG_BOX = (1395, 566, 1832, 590)   # grey tagline
RULE_Y = 547
LOCK_LEFT = 1403                   # wordmark left edge
LOCK_RIGHT = 1927                  # PRIVACY last stem


def flatten_bg(plate: Image.Image) -> None:
    """Background-level pixels become flat INK so no crop rectangle shows."""
    lum = plate.convert("L")
    plate.paste(Image.new("RGB", plate.size, INK), (0, 0),
                lum.point(lambda v: 255 if v <= 4 else 0))


def build() -> Image.Image:
    hero = Image.open(HERO).convert("RGB")
    plate = Image.new("RGB", (W, H), INK)

    for box in (GIRL_BOX, ROSE_BOX, GREEN_BOX, TAG_BOX):
        plate.paste(hero.crop(box), (box[0], box[1]))

    # the rule in the original runs 1521-1845: indented left of PRIVACY's stem
    # and 82px short of its last one. Draw it flush under the word instead.
    rule_color = hero.load()[1600, RULE_Y]
    plate.paste(Image.new("RGB", (LOCK_RIGHT - LOCK_LEFT, 2), rule_color),
                (LOCK_LEFT, RULE_Y))

    flatten_bg(plate)
    return plate


def render_preview(plate: Image.Image) -> Image.Image:
    """Theme-picker preview: the approved plate 1:1, centred on ink.

    The plate is 2560x1080 and this canvas is 2560x1440, so the band is
    padded with flat INK rather than upscaled - no invented pixels, no
    stretch, and the girl's scanlines stay exactly as they are.
    """
    canvas = Image.new("RGB", (2560, 1440), INK)
    canvas.paste(plate, (0, (1440 - plate.height) // 2))
    return canvas


def render_unlock(plate: Image.Image) -> Image.Image:
    """Lock surface: the girl 1:1 (no downscale, no glow), centred on ink.

    769x818 of real portrait inside a 1024 square. Scaling her down to fit
    the width would soften the hatching that IS the artwork, so she is
    pasted at 1:1 and the rest is ink.
    """
    girl = plate.crop(GIRL_BOX)
    canvas = Image.new("RGB", (1024, 1024), INK)
    canvas.paste(girl, ((1024 - girl.width) // 2, (1024 - girl.height) // 2))
    return canvas


if __name__ == "__main__":
    out = build()
    out.save(OUT, optimize=True)
    print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KiB)")

    preview = render_preview(out)
    preview.save(PREVIEW_OUT, optimize=True)
    print(f"wrote {PREVIEW_OUT.name} ({PREVIEW_OUT.stat().st_size // 1024} KiB)")

    unlock = render_unlock(out)
    unlock.save(UNLOCK_OUT, optimize=True)
    unlock.save(UNLOCK_PREVIEW_OUT, optimize=True)
    print(f"wrote {UNLOCK_OUT.name} + {UNLOCK_PREVIEW_OUT.name} "
          f"({UNLOCK_OUT.stat().st_size // 1024} KiB)")