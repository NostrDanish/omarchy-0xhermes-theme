#!/usr/bin/env python3
"""0xHermes v3 asset builder — wallpapers, lock art, and the animated saver.

Everything is drawn from scratch with Pillow and encoded with FFmpeg. No
network access, no third-party art.

    python3 tools/generate_v3_assets.py            # stills only
    python3 tools/generate_v3_assets.py --video    # + the 12 FPS saver loop
    python3 tools/generate_v3_assets.py --all

Outputs
    backgrounds/00-signal-temple.png   5120x2160  hero
    backgrounds/01-open-channel.png   5120x2160  quiet
    backgrounds/02-ghost-grid.png     5120x2160  grid-forward
    backgrounds/03-rose-protocol.png  5120x2160  rose-led
    backgrounds/0xhermes.png          5120x2160  byte-identical hero copy
    unlock.png / preview-unlock.png   1024x1024  lock surface
    preview.png                       2560x1440  theme-picker preview
    screensaver/hermes-signal.mp4     2560x1080  12 FPS seamless 12 s loop
    screensaver/mark.png              2560x1080  saver poster / fallback frame
"""
from __future__ import annotations

import argparse
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BACKGROUNDS = ROOT / "backgrounds"
SAVER = ROOT / "screensaver"

FONT_REGULAR = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"
FONT_FALLBACK = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"

INK = "#020804"          # forest black — the theme background
PHOSPHOR = "#39ff14"     # theme accent
MINT = "#83ff60"
ROSE = "#ff2e63"         # signal accent
FG = "#c7f5ce"           # theme foreground
MUTED = "#4b7d59"
TAU = math.tau

W, H = 5120, 2160


# --------------------------------------------------------------------------- helpers
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in ((FONT_BOLD if bold else FONT_REGULAR), FONT_FALLBACK):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:            # Pillow < 10.1
        return ImageFont.load_default()


def rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)) + (max(0, min(255, alpha)),)


def tracked(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str,
            face: ImageFont.FreeTypeFont, fill, tracking: float = 0.0) -> float:
    """Character-by-character text so mono caps can be optically tracked."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=face, fill=fill)
        x += draw.textlength(ch, font=face) + tracking
    return x


def glow(layer: Image.Image, radius: int, boost: float = 1.0) -> Image.Image:
    out = layer.filter(ImageFilter.GaussianBlur(radius))
    if boost != 1.0:
        out = Image.eval(out, lambda v: min(255, int(v * boost)))
    return out


def soft_blob(w: int, h: int, center: tuple[float, float], radius: float,
              color: str, alpha: int, blur: float) -> Image.Image:
    """Big soft light, rendered small and upscaled — cheap Gaussian."""
    k = 4
    sw, sh = max(2, w // k), max(2, h // k)
    small = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    cx, cy, r = center[0] / k, center[1] / k, radius / k
    ImageDraw.Draw(small).ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba(color, alpha))
    small = small.filter(ImageFilter.GaussianBlur(max(1, blur / k)))
    return small.resize((w, h), Image.Resampling.BILINEAR)


# --------------------------------------------------------------------------- field
def substrate(w: int, h: int, rose_bias: float = 0.0,
              well: tuple[float, float] = (0.62, 0.44)) -> Image.Image:
    """Deep forest field with a green signal well and a rose counterweight."""
    sw = 480
    sh = max(160, round(sw * h / w))
    field = Image.new("RGB", (sw, sh))
    px = field.load()
    wx, wy = well
    for y in range(sh):
        ny = y / max(1, sh - 1)
        for x in range(sw):
            nx = x / max(1, sw - 1)
            dg = ((nx - wx) / 0.52) ** 2 + ((ny - wy) / 0.62) ** 2
            dr = ((nx - 0.04) / 0.46) ** 2 + ((ny - 1.08) / 0.44) ** 2
            green = math.exp(-2.7 * dg) * (1.0 - 0.45 * rose_bias)
            pink = math.exp(-3.4 * dr) * (0.34 + 0.66 * rose_bias)
            edge = min(1.0, max(0.0, ((abs(nx - 0.5) * 1.9) ** 2 + (abs(ny - 0.5) * 1.5) ** 2) - 0.18))
            shade = 1.0 - 0.52 * edge
            r = (3 + 10 * pink + 2 * green) * shade
            g = (8 + 36 * green + 3 * pink) * shade
            b = (7 + 17 * green + 13 * pink) * shade
            px[x, y] = (max(1, int(r)), max(2, int(g)), max(2, int(b)))

    field = field.resize((w, h), Image.Resampling.BICUBIC).convert("RGBA")

    # Fine dither: kills 8-bit banding in the gradients without visible grain.
    rnd = random.Random(7717)
    noise = Image.new("L", (max(2, w // 3), max(2, h // 3)))
    noise.putdata([128 + rnd.randint(-9, 9) for _ in range(noise.width * noise.height)])
    noise = noise.resize((w, h), Image.Resampling.NEAREST)
    grain = Image.merge("RGBA", (noise, noise, noise, Image.new("L", (w, h), 12)))
    return ImageChops.add(field, grain, scale=1.0, offset=-128)


def grid_layer(w: int, h: int, step: int = 64, alpha: int = 10, major_every: int = 5,
               fade: float = 0.55) -> Image.Image:
    """Technical grid that falls away toward the edges so it never fights the bar."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, w + 1, step):
        major = (x // step) % major_every == 0
        d.line((x, 0, x, h), fill=rgba(PHOSPHOR, alpha + (7 if major else 0)), width=1)
    for y in range(0, h + 1, step):
        major = (y // step) % major_every == 0
        d.line((0, y, w, y), fill=rgba(PHOSPHOR, alpha + (7 if major else 0)), width=1)

    inset = fade * 0.22
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse(
        (-w * inset, -h * (inset + 0.04), w * (1 + inset), h * (1 + inset)), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(10, w // 34)))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    return layer


def centerline(w: int, h: int, y: float, color: str, alpha: int = 22,
               fade: float = 0.60) -> Image.Image:
    """Full-bleed horizon through the sigil: the line that ties a 21:9 frame together."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line((0, y, w, y), fill=rgba(color, alpha), width=2)
    for x in range(0, w, 48):
        ln = 16 if (x // 48) % 5 == 0 else 7
        d.line((x, y - ln, x, y + 2), fill=rgba(color, max(8, alpha - 4)), width=1)
    for x in range(0, w, 48):
        ln = 11 if (x // 48) % 5 == 0 else 5
        d.line((x, y - ln, x, y + 2), fill=rgba(color, max(6, alpha - 8)), width=1)

    inset = fade * 0.18
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((-w * inset, -h * 0.9, w * (1 + inset), h * 1.9), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(12, w // 40)))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    return layer


def waveform(w: int, h: int, y: float, seed: int = 31, amp: float = 44,
             rose: bool = False) -> Image.Image:
    """An instrument trace running the whole width — horizontal weight for the plate."""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    phase = [rnd.uniform(0, TAU) for _ in range(4)]

    def sample(x: float, k: float = 1.0) -> float:
        nx = x / w
        base = (math.sin(nx * 11.0 + phase[0]) * 0.55
                + math.sin(nx * 27.0 + phase[1]) * 0.30
                + math.sin(nx * 61.0 + phase[2]) * 0.15)
        envelope = 0.28 + 0.72 * (math.sin(nx * 3.3 + phase[3]) * 0.5 + 0.5) ** 1.6
        return base * envelope * amp * k

    step = 4
    pts = [(x, y + sample(x)) for x in range(0, w + step, step)]
    d.line(pts, fill=rgba(ROSE if rose else PHOSPHOR, 96), width=2, joint="curve")
    d.line([(x, y + 0.55 * (py - y)) for x, py in pts],
           fill=rgba(ROSE if rose else PHOSPHOR, 40), width=1)
    image_pts = [(x, y + sample(x, 1.0)) for x in range(0, w + step, step * 4)]
    for x, py in image_pts:
        d.line((x, py, x, y), fill=rgba(ROSE if rose else PHOSPHOR, 16), width=1)
    for x in range(0, w, 320):
        tracked(d, (x + 8, y + amp + 26), f"{(x // 320) * 2:04d}", font(15),
                rgba(MUTED, 90), 2)
    return layer


def conduit(w: int, h: int, x0: float, y0: float, x1: float, y1: float,
            color: str) -> Image.Image:
    """Dashed connector from the type block to the sigil: kills the dead middle."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    midx = (x0 + x1) / 2
    pts = [(x0, y0), (midx, y0), (midx, y1), (x1, y1)]
    d.line(pts, fill=rgba(color, 46), width=2, joint="curve")
    for i in range(14):
        t = (i + 0.5) / 14
        x = x0 + (midx - x0) * t
        d.line((x, y0, x + 8, y0), fill=rgba(color, 110), width=3)
    for px, py in ((midx, y0), (midx, y1)):
        d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=rgba(color, 150))
    return layer


def dust(w: int, h: int, count: int, seed: int, center: tuple[float, float],
         spread: tuple[float, float]) -> Image.Image:
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(count):
        a = rnd.random() * TAU
        rad = rnd.random() ** 0.72
        x = center[0] + math.cos(a) * rad * spread[0]
        y = center[1] + math.sin(a) * rad * spread[1] * 0.62
        if not (0 <= x < w and 0 <= y < h):
            continue
        size = rnd.choice((1, 1, 1, 2, 2, 3))
        color = ROSE if i % 19 == 0 else (MINT if i % 3 == 0 else PHOSPHOR)
        d.ellipse((x, y, x + size, y + size), fill=rgba(color, rnd.randint(40, 150)))
    return layer


def scanlines(w: int, h: int, period: int = 4, alpha: int = 6) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, h, period):
        d.line((0, y, w, y), fill=(0, 0, 0, alpha), width=1)
    return layer


def shelf(w: int, h: int, depth: int = 228, strength: int = 104) -> Image.Image:
    """Dark shelves top and bottom: keeps the bar and the type legible."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(depth):
        a = round(strength * (1 - i / depth) ** 2.4)
        d.line((0, i, w, i), fill=(0, 3, 2, a))
        d.line((0, h - 1 - i, w, h - 1 - i), fill=(0, 3, 2, a))
    return layer


# --------------------------------------------------------------------------- sigil
def dashed_arc(d: ImageDraw.ImageDraw, box, start: float, end: float, fill, width: int,
               dash: float = 3.2, gap: float = 4.4) -> None:
    a = start
    while a < end:
        d.arc(box, a, min(a + dash, end), fill=fill, width=width)
        a += dash + gap


def hermes_sigil(size: int, rose_ring: bool = False, bright: bool = True) -> Image.Image:
    """A winged H inside a hexagonal aperture — the theme's mark."""
    s = size / 1000.0
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = cy = size / 2
    core = rgba(MINT if bright else FG, 238)
    mid = rgba(PHOSPHOR, 152)
    dim = rgba(PHOSPHOR, 64)
    rose = rgba(ROSE, 230)
    hair = max(1, round(2 * s))

    def box(r: float):
        return (cx - r * s, cy - r * s, cx + r * s, cy + r * s)

    # reticles
    for r, a in ((470, 44), (432, 30), (392, 70)):
        d.ellipse(box(r), outline=rgba(PHOSPHOR, a), width=hair)
    for r, a in ((448, 54), (410, 34)):
        dashed_arc(d, box(r), 12, 168, rgba(PHOSPHOR, a), hair)
        dashed_arc(d, box(r), 192, 348, rgba(ROSE if rose_ring else PHOSPHOR, a), hair)

    # radial ticks
    for i in range(72):
        ang = TAU * i / 72
        r2 = 496 if i % 6 == 0 else 480
        d.line((cx + math.cos(ang) * 470 * s, cy + math.sin(ang) * 470 * s,
                cx + math.cos(ang) * r2 * s, cy + math.sin(ang) * r2 * s),
               fill=rgba(PHOSPHOR, 92 if i % 6 == 0 else 34), width=hair)

    # hexagonal aperture
    for r, a, wd in ((340, 122, max(2, round(3 * s))), (316, 48, hair)):
        hexa = [(cx + math.cos(TAU * i / 6 - math.pi / 2) * r * s,
                 cy + math.sin(TAU * i / 6 - math.pi / 2) * r * s) for i in range(6)]
        d.line(hexa + [hexa[0]], fill=rgba(ROSE if (rose_ring and r == 316) else PHOSPHOR, a),
               width=wd, joint="curve")

    # wings: three rising strokes per side
    for side in (-1, 1):
        for i in range(3):
            y = cy + (-118 + i * 84) * s
            d.line([(cx + side * 96 * s, y + 40 * s),
                    (cx + side * (222 + i * 20) * s, y - (50 - i * 11) * s),
                    (cx + side * (322 + i * 13) * s, y - (26 - i * 8) * s)],
                   fill=core if side == 1 else mid,
                   width=max(2, round((8 - i * 1.4) * s)), joint="curve")
        d.line((cx + side * 108 * s, cy - 176 * s, cx + side * 108 * s, cy + 190 * s),
               fill=core, width=max(2, round(9 * s)))

    # the H
    d.line((cx - 252 * s, cy + 6 * s, cx + 252 * s, cy + 6 * s), fill=core,
           width=max(2, round(9 * s)))
    d.line((cx, cy - 210 * s, cx, cy + 214 * s), fill=rgba(MINT, 120), width=hair)
    r = 26 * s
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba(INK, 255), outline=rose,
              width=max(2, round(6 * s)))
    r = 6 * s
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rose)

    # signal nodes
    for x, y, color in ((-352, -150, mid), (378, 116, rose), (-286, 218, dim), (286, -214, dim)):
        rr = 6 * s
        d.ellipse((cx + x * s - rr, cy + y * s - rr, cx + x * s + rr, cy + y * s + rr), fill=color)
    return layer


def orbits(size: int, rose_mix: float = 0.0) -> Image.Image:
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = size / 2
    for i in range(9):
        rx = size * (0.335 + i * 0.070)
        ry = rx * 0.42
        start = (i * 41 + 8) % 360
        color = ROSE if (i % 3 == 0 and rose_mix > 0.2) else PHOSPHOR
        a = max(12, 64 - i * 5)
        d.arc((c - rx, c - ry, c + rx, c + ry), start, start + 212, fill=rgba(color, a), width=2)
        if i % 2 == 0:
            dashed_arc(d, (c - rx, c - ry, c + rx, c + ry), start + 224, start + 348,
                       rgba(color, a // 2), 2, 2.4, 5.0)
    return layer


# --------------------------------------------------------------------------- wallpapers
def compose_hero(rose: bool = False, quiet: bool = False,
                 grid_forward: bool = False) -> Image.Image:
    accent = ROSE if rose else PHOSPHOR
    image = substrate(W, H, rose_bias=0.85 if rose else 0.0,
                      well=(0.5, 0.5) if grid_forward else (0.68, 0.42))

    grid = grid_layer(W, H, 64, 34 if grid_forward else 12, 5,
                      0.20 if grid_forward else 0.6)
    image.alpha_composite(grid)
    del grid

    sy_center = int(H * 0.455)

    # full-bleed horizon through the sigil — the spine of a 21:9 frame
    if not grid_forward:
        cl = centerline(W, H, sy_center, accent, 26 if rose else 24)
        image.alpha_composite(cl)
        del cl

    sx = int(W * 0.715)
    if not grid_forward:
        image.alpha_composite(soft_blob(W, H, (sx, sy_center), 780,
                                        accent, 50, 460))
        sig = hermes_sigil(1700, rose_ring=rose)
        image.alpha_composite(sig, (sx - 850, sy_center - 850))
        del sig
        orb = orbits(3800, 1.0 if rose else 0.0)
        image.alpha_composite(orb, (sx - 1900, sy_center - 1900))
        del orb
        dst = dust(W, H, 360, 4242 if rose else 2024, (sx, sy_center), (1800, 1800))
        image.alpha_composite(dst)
        del dst
    else:
        # ghost mark: the sigil at a fraction of its opacity, as a watermark
        water = hermes_sigil(1500)
        water.putalpha(water.getchannel("A").point(lambda v: int(v * 0.15)))
        image.alpha_composite(water, (int(W * 0.5) - 750, sy_center - 750))
        del water
        dst = dust(W, H, 460, 909, (W * 0.5, H * 0.46), (2100, 1200))
        image.alpha_composite(dst)
        del dst

    # instrument trace across the whole width
    wf = waveform(W, H, H * 0.735, 31 if not rose else 57, 42, rose=rose)
    image.alpha_composite(glow(wf, 14, 1.2))
    image.alpha_composite(wf)
    del wf

    # typography, inside the safe zone of the 26 px top bar
    text = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(text)
    x, y = 250, 985

    if quiet:
        tracked(td, (x, sy_center - 30), "OPEN CHANNEL / CLOSED LOOP", font(30), rgba(MUTED, 205), 5)
        tracked(td, (x, sy_center + 28), "0xHERMES // SIGNAL TEMPLE", font(22),
                rgba(PHOSPHOR, 152), 4)
    elif grid_forward:
        tracked(td, (x, H - 268), "0xHERMES  /  GHOST GRID", font(25), rgba(MUTED, 158), 4)
        tracked(td, (x, H - 220), "NOISE FLOOR: -112 dBm", font(19), rgba(PHOSPHOR, 112), 3)
        for i, line in enumerate(("RX / 5120 x 2160", "GAIN 0.0 dB", "HOLD: 12 s")):
            tracked(td, (W - 470, H * 0.13 + i * 34), line, font(18), rgba(MUTED, 140), 3)
    else:
        tracked(td, (x, y), "PRIVATE INTELLIGENCE / 03", font(26), rgba(MUTED, 228), 6)
        tracked(td, (x - 8, y + 70), "0x", font(124, True), rgba(ROSE, 255), 2)
        tracked(td, (x + 176, y + 20), "HERMES", font(162, True), rgba(FG, 255), 9)
        td.line((x, y + 234, x + 1010, y + 234), fill=rgba(accent, 120), width=2)
        tracked(td, (x, y + 276), "SIGNAL TEMPLE  /  NO TELEMETRY", font(31), rgba(PHOSPHOR, 222), 4)
        tracked(td, (x, H - 176), "0xHERMES V3  //  OMARCHY EDITION", font(21), rgba(MUTED, 172), 4)
        tracked(td, (W - 800, H - 176), "NODE: DESKTOP  //  LOCAL ONLY", font(19), rgba(MUTED, 136), 3)

        # connector from the rule into the sigil, so the middle isn't dead air
        con = conduit(W, H, x + 1018, y + 234, sx - 900, sy_center + 300, accent)
        image.alpha_composite(con)
        del con

    image.alpha_composite(glow(text, 26, 1.35))
    image.alpha_composite(text)
    del text

    sl = scanlines(W, H, 4, 7)
    image.alpha_composite(sl)
    del sl
    sh = shelf(W, H)
    image.alpha_composite(sh)
    del sh

    # vignette
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.22, -H * 0.30, W * 1.22, H * 1.30), fill=255)
    dark = Image.new("RGBA", (W, H), (0, 2, 1, 150))
    dark.putalpha(ImageChops.invert(vig.point(lambda v: v)).point(lambda v: int(v * 0.55)))
    del vig
    image.alpha_composite(dark)
    del dark
    return image.convert("RGB")


def lock_art() -> Image.Image:
    """1024² lock surface. Everything lives above 62% height: the password field
    and its status line are drawn by the greeter in the clean lower area."""
    size = 1024
    image = substrate(size, size, rose_bias=0.25, well=(0.5, 0.30))
    gl = grid_layer(size, size, 48, 12, 4, 0.55)
    image.alpha_composite(gl)
    del gl
    image.alpha_composite(soft_blob(size, size, (512, 300), 300, PHOSPHOR, 46, 190))
    image.alpha_composite(hermes_sigil(430), (297, 85))

    d = ImageDraw.Draw(image)
    tracked(d, (54, 44), "0xHERMES / V3", font(15), rgba(MUTED, 150), 3)
    tracked(d, (size - 232, 44), "LOCAL ONLY", font(15), rgba(MUTED, 150), 3)

    title = "0xHERMES"
    face = font(58, True)
    tw = d.textlength(title, font=face)
    d.text(((size - tw) / 2, 548), title, font=face, fill=rgba(FG, 255))
    tracked(d, (352, 634), "PRIVATE INTELLIGENCE", font(16), rgba(PHOSPHOR, 200), 3)
    d.line((392, 676, 632, 676), fill=rgba(ROSE, 150), width=2)
    image.alpha_composite(scanlines(size, size, 3, 6))
    return image.convert("RGB")


# --------------------------------------------------------------------------- saver
def saver_base(w: int, h: int) -> Image.Image:
    image = substrate(w, h, well=(0.5, 0.42))
    gl = grid_layer(w, h, 48, 10, 5, 0.45)
    image.alpha_composite(gl)
    del gl
    cl = centerline(w, h, int(h * 0.455), PHOSPHOR, 20)
    image.alpha_composite(cl)
    del cl
    d = ImageDraw.Draw(image)
    tracked(d, (64, 46), "0x / IDLE CHANNEL", font(17), rgba(MUTED, 132), 3)
    tracked(d, (w - 452, h - 64), "PRIVATE / LOCAL / YOURS", font(16), rgba(MUTED, 120), 2)
    image.alpha_composite(scanlines(w, h, 4, 6))
    return image


def saver_frame(t: float, w: int, h: int, base: Image.Image, halo: Image.Image,
                ring: Image.Image, core: Image.Image, label: Image.Image,
                packets: list[tuple[float, float, float, str]]) -> Image.Image:
    """t in [0,1). Every motion completes a whole number of cycles, so it loops."""
    phase = t * TAU
    image = base.copy()
    cx, cy = w * 0.5, h * 0.455

    image.alpha_composite(halo, (0, 0))
    ring_rot = ring.rotate(-360 * t, resample=Image.Resampling.BICUBIC)
    image.alpha_composite(ring_rot, (round(cx - ring.width / 2), round(cy - ring.height / 2)))
    image.alpha_composite(core, (round(cx - core.width / 2), round(cy - core.height / 2)))
    image.alpha_composite(label, (round(cx - label.width / 2), round(cy + 292)))

    # packets on closed orbits (integer turns -> seamless)
    pl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pl)
    for radius, turns, offset, color in packets:
        a = phase * turns + offset
        x = cx + math.cos(a) * radius
        y = cy + math.sin(a) * radius * 0.62
        pd.ellipse((x - 12, y - 12, x + 12, y + 12), fill=rgba(color, 46))
        pd.ellipse((x - 4, y - 4, x + 4, y + 4), fill=rgba(color, 214))
    image.alpha_composite(pl.filter(ImageFilter.GaussianBlur(3)))
    image.alpha_composite(pl)
    del pl

    # scanner sweep: fully off-canvas at both ends of the loop
    scan = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    sx = -w * 0.35 + (w * 1.7) * t
    sd.polygon(((sx - 110, 0), (sx + 10, 0), (sx + 250, h), (sx + 130, h)),
               fill=rgba(PHOSPHOR, 10))
    sd.line((sx + 10, 0, sx + 250, h), fill=rgba(ROSE, 36), width=2)
    image.alpha_composite(scan)
    del scan
    return image.convert("RGB")


def build_saver(w: int = 2560, h: int = 1080, fps: int = 12, seconds: int = 12,
                encode: bool = True) -> Image.Image:
    base = saver_base(w, h)
    halo = soft_blob(w, h, (w * 0.5, h * 0.455), 430, PHOSPHOR, 42, 300)
    ring_img = hermes_sigil(900, rose_ring=True)
    core_img = hermes_sigil(560, bright=True)

    label = Image.new("RGBA", (1024, 180), (0, 0, 0, 0))
    ld = ImageDraw.Draw(label)
    tracked(ld, (188, 0), "0xHERMES", font(64, True), rgba(FG, 248), 6)
    tracked(ld, (208, 94), "SIGNAL / PRIVATE / LOCAL", font(19), rgba(PHOSPHOR, 182), 3)

    packets = [(330.0, 1.0, 0.0, PHOSPHOR),
               (430.0, -1.0, 1.9, ROSE),
               (530.0, 2.0, 3.6, MINT)]

    poster = saver_frame(0.0, w, h, base, halo, ring_img, core_img, label, packets)
    poster.save(SAVER / "mark.png", optimize=True)
    poster.save(SAVER / "preview.png", optimize=True)

    if not encode:
        return poster

    frames = fps * seconds
    out = SAVER / "hermes-signal.mp4"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(fps), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
           "-pix_fmt", "yuv420p", "-g", str(fps * 2), "-movflags", "+faststart",
           "-metadata", "title=0xHermes v3 - Signal Temple", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(frames):
            frame = saver_frame(i / frames, w, h, base, halo, ring_img, core_img, label, packets)
            proc.stdin.write(frame.tobytes())
            if i % 24 == 0:
                print(f"  saver {i:03d}/{frames}", flush=True)
    except BrokenPipeError:
        pass
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed to encode the saver loop")
    print(f"  wrote {out.name} ({out.stat().st_size // 1024} KiB)")
    return poster


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", action="store_true", help="also encode the saver loop")
    ap.add_argument("--stills", action="store_true", help="wallpapers + lock + previews")
    ap.add_argument("--all", action="store_true", help="stills and the saver loop")
    args = ap.parse_args()
    if args.all:
        args.stills = args.video = True
    if not args.video and not args.stills:
        args.stills = True
    if not Path(FONT_REGULAR).exists():
        print(f"  note: {FONT_REGULAR} missing, falling back to {FONT_FALLBACK}")

    BACKGROUNDS.mkdir(parents=True, exist_ok=True)
    SAVER.mkdir(parents=True, exist_ok=True)

    if args.stills:
        hero = compose_hero()
        hero.save(BACKGROUNDS / "00-signal-temple.png", optimize=True)
        print("  wrote 00-signal-temple.png")
        compose_hero(quiet=True).save(BACKGROUNDS / "01-open-channel.png", optimize=True)
        print("  wrote 01-open-channel.png")
        compose_hero(grid_forward=True).save(BACKGROUNDS / "02-ghost-grid.png", optimize=True)
        print("  wrote 02-ghost-grid.png")
        compose_hero(rose=True).save(BACKGROUNDS / "03-rose-protocol.png", optimize=True)
        print("  wrote 03-rose-protocol.png")

        # the picker anchor stays a byte-identical copy of the hero
        (BACKGROUNDS / "0xhermes.png").write_bytes(
            (BACKGROUNDS / "00-signal-temple.png").read_bytes())

        lock = lock_art()
        lock.save(ROOT / "unlock.png", optimize=True)
        lock.save(ROOT / "preview-unlock.png", optimize=True)
        print("  wrote unlock.png")

        ImageOps.fit(hero, (2560, 1440), method=Image.Resampling.LANCZOS,
                     centering=(0.55, 0.5)).save(ROOT / "preview.png", optimize=True)
        print("  wrote preview.png")

    if args.video:
        build_saver(encode=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
