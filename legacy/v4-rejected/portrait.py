#!/usr/bin/env python3
"""0xHermes dot-matrix portrait renderer.

Provenance of the girl portrait
-------------------------------
There is no generator for it anywhere: not in this repo's git history
(`git log --all --diff-filter=D --name-only` shows only the PNG/MP4 that were
replaced by the v3 revert), not in `legacy/v2-first-pass|second-pass/`, and not
upstream — commit 299aec7 added only the rendered `backgrounds/0xhermes.png`,
and both committed generators (generate_v2_assets.py, generate_v3_assets.py)
build the abstract "signal temple" plates and never a face.

So the portrait is recovered from the luminance of
`backgrounds/0xhermes.png` itself, which is a monochrome phosphor-green
dot-matrix image and therefore a valid luminance map. PORTRAIT_BOX is the
recovered bounding box of the girl in that image (green-pixel bbox, stable at
both a bright and a dim threshold).

Public API
----------
render(canvas_size, region, matrix_density=200, palette=None, glow=0.6) -> Image
    RGBA image of `canvas_size` with the girl drawn as a dot matrix fitted,
    aspect-preserved and centred, inside `region`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backgrounds" / "0xhermes.png"

# Recovered girl silhouette inside SOURCE: green-pixel bbox x 631..1327, y 122..939.
PORTRAIT_BOX = (631, 122, 1328, 940)

# Palette of the source wallpaper.
INK = "#020804"
PHOSPHOR = "#39ff14"
GLOW = "#39ff14"
DEFAULT_PALETTE = {"ink": INK, "phosphor": PHOSPHOR, "glow": GLOW}

# Luminance window that maps to dot opacity: below LO is empty, at HI a dot is solid.
LUM_LO, LUM_HI = 15, 122
DOT_FILL = 0.6  # dot side as a fraction of the grid pitch, leaving a dark gutter


def _hex(value: str) -> tuple[int, ...]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _source_luminance() -> Image.Image:
    """The portrait as an 8-bit luminance map, cropped from the frozen hero."""
    return Image.open(SOURCE).convert("L").crop(PORTRAIT_BOX)


def render(
    canvas_size: tuple[int, int],
    region: tuple[int, int, int, int],
    matrix_density: int = 200,
    palette: dict[str, str] | None = None,
    glow: float = 0.6,
) -> Image.Image:
    """Draw the 0xHermes girl as a dot matrix inside `region`.

    canvas_size     (width, height) of the returned RGBA layer.
    region          (x, y, width, height) box the portrait is fitted into;
                    the source aspect is preserved and the portrait centred.
    matrix_density  number of dot rows down the portrait (higher = finer).
    palette         overrides for INK / PHOSPHOR / GLOW hex colours.
    glow            bloom strength 0..1 (0 disables the halo).
    """
    pal = {**DEFAULT_PALETTE, **(palette or {})}
    width, height = canvas_size
    rx, ry, rw, rh = region

    src = _source_luminance()
    sw, sh = src.size
    aspect = sw / sh

    # Aspect-preserving fit, centred in the region box.
    if rw / rh > aspect:
        dw, dh = max(1, round(rh * aspect)), rh
    else:
        dw, dh = rw, max(1, round(rw / aspect))
    ox, oy = rx + (rw - dw) // 2, ry + (rh - dh) // 2

    # Dot grid derived from the target resolution: density sets the rows, the
    # source aspect sets the columns, the fitted height sets the pixel pitch.
    rows = max(4, int(matrix_density))
    cols = max(1, round(rows * aspect))
    pitch = max(1, round(dh / rows))
    side = max(1, round(pitch * DOT_FILL))

    lum = src.resize((cols, rows), Image.Resampling.LANCZOS).load()
    pr, pg, pb = _hex(pal["phosphor"])

    dots = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    d = ImageDraw.Draw(dots)
    for gy in range(rows):
        cy = oy + gy * pitch + (pitch - side) // 2
        for gx in range(cols):
            level = lum[gx, gy]
            if level <= LUM_LO:
                continue
            a = (level - LUM_LO) / (LUM_HI - LUM_LO)
            a = 0.0 if a < 0 else 1.0 if a > 1 else a
            cx = ox + gx * pitch + (pitch - side) // 2
            d.rectangle((cx, cy, cx + side - 1, cy + side - 1), fill=(pr, pg, pb, int(255 * a)))

    layer = Image.new("RGBA", canvas_size, _hex(pal["ink"]) + (255,))
    if glow > 0:
        halo = dots.filter(ImageFilter.GaussianBlur(max(1.0, pitch * 1.4)))
        tint = Image.new("RGBA", canvas_size, _hex(pal["glow"]) + (0,))
        tint.putalpha(halo.getchannel("A").point(lambda v: int(v * glow)))
        layer = Image.alpha_composite(layer, tint)
    return Image.alpha_composite(layer, dots)


SELFTEST_OUT = Path("/home/master/.hermes/cache/scratch/portrait-selftest.png")
SELFTEST_CANVAS = (2560, 1080)
SELFTEST_REGION = (160, 60, 900, 960)  # portrait on the left half


def _selftest() -> int:
    img = render(SELFTEST_CANVAS, SELFTEST_REGION)
    SELFTEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(SELFTEST_OUT)

    assert img.size == SELFTEST_CANVAS, img.size
    assert img.mode == "RGBA", img.mode

    px = img.convert("RGB").load()
    w, h = SELFTEST_CANVAS
    bx0, by0, bx1, by1 = 200, 55, 1025, 1025  # slop around the fitted portrait

    dots = 0
    bg_sum = [0, 0, 0]
    bg_n = 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            inside = bx0 <= x < bx1 and by0 <= y < by1
            green = g > 120 and g > r + 40 and g > b + 40
            if inside:
                dots += green
            else:
                bg_sum[0] += r
                bg_sum[1] += g
                bg_sum[2] += b
                bg_n += 1
    area = (bx1 - bx0) * (by1 - by0)
    coverage = dots / area
    bg = tuple(s / bg_n for s in bg_sum)
    ink = _hex(INK)

    print(f"wrote {SELFTEST_OUT}")
    print(f"dot coverage in portrait box: {coverage:.3%} ({dots} px)")
    print(f"background mean RGB: ({bg[0]:.2f}, {bg[1]:.2f}, {bg[2]:.2f}) vs ink {ink}")

    assert coverage > 0.05, f"portrait too sparse: {coverage:.3%}"
    for got, want in zip(bg, ink):
        assert abs(got - want) <= 4, f"background drifted from ink: {bg} vs {ink}"
    print("selftest OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true", help="render the 2560x1080 left-half check")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
