#!/usr/bin/env python3
"""0xHermes v4 — the dot-matrix portrait system, executed at 5K.

Implements docs/v4-brief.md exactly: ink + phosphor carry the weight, rose
appears once per level, the portrait is a hard-grid dot matrix recovered from
the frozen hero's luminance (see tools/portrait.py for provenance), and the
saver loop uses only periodic transforms so frame 0 == frame 143.

    python3 tools/generate_v4_assets.py            # three stills + lock + preview
    python3 tools/generate_v4_assets.py --video    # + the 144-frame saver loop

Outputs (the loved 0xhermes.png set is never touched)
    backgrounds/20-dot-matrix-hero.png     5120x2160
    backgrounds/21-quiet-channel.png      5120x2160
    backgrounds/22-cipher-storm.png       5120x2160
    unlock.png / preview-unlock.png       1024x1024
    preview.png                           2560x1440
    screensaver/hermes-dots.mp4           2560x1080, 12 FPS, seamless 12 s
    screensaver/mark.png                  saver poster
"""
from __future__ import annotations

import argparse
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import portrait  # noqa: E402  (reuses the recovered luminance source + bbox)

ROOT = Path(__file__).resolve().parents[1]
BACKGROUNDS = ROOT / "backgrounds"
SAVER = ROOT / "screensaver"

FONT_REGULAR = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"
FONT_FALLBACK = "/usr/share/fonts/TTF/DejaVuSansMono.ttf"

INK = "#020804"
VOID = "#000000"
SHADOW = "#010402"
PHOSPHOR = "#39ff14"
MINT = "#83ff60"
ROSE = "#ff2e63"
FG = "#c7f5ce"
MUTED = "#426b4b"
TAU = math.tau

W, H = 5120, 2160
FRAMES, FPS = 144, 12
SW, SH = 2560, 1080  # saver canvas


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in ((FONT_BOLD if bold else FONT_REGULAR), FONT_FALLBACK):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) + (max(0, min(255, alpha)),)


def tracked(d, xy, text, face, fill, tracking=0.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=face, fill=fill)
        x += d.textlength(ch, font=face) + tracking
    return x


# ------------------------------------------------------------------ dot matrix
def luminance_crop(box=None) -> Image.Image:
    src = portrait._source_luminance()
    return src.crop(box) if box else src


def dots_layer(size, region, rows, lum=None, pitch_override=None,
               color=PHOSPHOR, lo=15, hi=122, fill=0.75, seed=None,
               jitter_px=0, jitter_rate=0.0):
    """Hard-grid dot matrix of `lum` fitted inside region. Transparent RGBA.

    jitter_* reproduces the storm variant's frozen spatial glitch (brief 7.3).
    """
    lum = lum if lum is not None else luminance_crop()
    w, h = size
    rx, ry, rw, rh = region
    sw, sh = lum.size
    aspect = sw / sh
    dw, dh = (round(rh * aspect), rh) if rw / rh > aspect else (rw, round(rw / aspect))
    ox, oy = rx + (rw - dw) // 2, ry + (rh - dh) // 2

    rows = max(4, rows)
    cols = max(1, round(rows * aspect))
    pitch = pitch_override or max(1, round(dh / rows))
    side = max(1, round(pitch * fill))
    grid = lum.resize((cols, rows), Image.Resampling.LANCZOS).load()

    rnd = random.Random(seed)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pr, pg, pb = rgba(color, 255)[:3]
    for gy in range(rows):
        cy = oy + gy * pitch + (pitch - side) // 2
        for gx in range(cols):
            level = grid[gx, gy]
            if level <= lo:
                continue
            a = min(1.0, max(0.0, (level - lo) / (hi - lo)))
            cx = ox + gx * pitch + (pitch - side) // 2
            if jitter_px and rnd.random() < jitter_rate:
                cx += rnd.randint(-jitter_px, jitter_px)
            d.rectangle((cx, cy, cx + side - 1, cy + side - 1),
                        fill=(pr, pg, pb, int(255 * a)))
    return layer


# ------------------------------------------------------------------ atmosphere
def vignette(size, strength=38) -> Image.Image:
    w, h = size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((-w * 0.22, -h * 0.30, w * 1.22, h * 1.30), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(10, w // 40)))
    dark = Image.new("RGBA", (w, h), rgba(SHADOW, 255))
    dark.putalpha(ImageChops.invert(mask).point(lambda v: int(v * strength / 255)))
    return dark


def scanlines(size, spacing=3, alpha=8) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, h, spacing):
        d.line((0, y, w, y), fill=rgba(PHOSPHOR, alpha), width=1)
    return layer


def grain(size, alpha=3, seed=99) -> Image.Image:
    w, h = size
    rnd = random.Random(seed)
    tile = Image.new("L", (64, 64))
    tile.putdata([rnd.randint(0, 255) for _ in range(64 * 64)])
    noise = Image.new("L", (w, h))
    for y in range(0, h, 64):
        for x in range(0, w, 64):
            noise.paste(tile, (x, y))
    layer = Image.new("RGBA", (w, h), rgba(PHOSPHOR, 0))
    layer.putalpha(noise.point(lambda v: int(v * alpha / 255)))
    return layer


def edge_columns(size, alpha=15, seed=5) -> Image.Image:
    """Binary/hex columns hugging the left and right edges, 120 px linear fade."""
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    face = font(14)
    rnd = random.Random(seed)
    y0, y1 = 200, h - 360
    for x, align_right in ((20, False), (w - 34, True)):
        chars = [rnd.choice("0123456789ABCDEF") for _ in range((y1 - y0) // 18)]
        text = "".join(chars)
        col = Image.new("RGBA", (24, y1 - y0), (0, 0, 0, 0))
        cd = ImageDraw.Draw(col)
        for i, ch in enumerate(text):
            cd.text((0, i * 18), ch, font=face, fill=rgba(PHOSPHOR, 255))
        fade = Image.new("L", col.size, 0)
        fd = ImageDraw.Draw(fade)
        for i in range(len(text)):
            t = i * 18
            edge_dist = min(t, col.height - t)
            a = int(255 * min(1.0, edge_dist / 120))
            fd.rectangle((0, t, 24, t + 18), fill=a)
        col.putalpha(ImageChops.multiply(col.getchannel("A"), fade))
        layer.alpha_composite(col, (x, y0))
    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha / 255)))
    return layer


# ------------------------------------------------------------------ type block
def type_block(size, quiet=False, storm=False, scale=1.0) -> Image.Image:
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def S(v):
        return round(v * scale)

    if quiet:
        tracked(d, (S(1600), S(760)), "0x", font(S(220), True), rgba(ROSE, 255), S(2))
        tracked(d, (S(1880), S(760)), "PRIVACY", font(S(220), True), rgba(MUTED, 255), S(40))
        return layer

    tracked(d, (S(1600), S(760)), "0x", font(S(220), True), rgba(ROSE, 255), S(2))
    tracked(d, (S(1880), S(760)), "PRIVACY", font(S(220), True), rgba(PHOSPHOR, 255), S(40))
    d.rectangle((S(1600), S(1000), S(1600) + S(1120), S(1000) + S(4)), fill=rgba(ROSE, 255))
    tagline = "TRUST NOTHING . VERIFY EVERYTHING" if storm else "NO LOGS . NO TRACE . NO NAME"
    tracked(d, (S(1600), S(1120)), tagline, font(S(38)), rgba(FG, 235), S(12))
    tracked(d, (S(40), h - S(80)), "0xPRIVACY", font(S(22)), rgba(MUTED, 200), S(3))
    root = "ROOT"
    face = font(S(22))
    width = sum(d.textlength(c, font=face) + S(3) for c in root)
    tracked(d, (w - S(40) - width, h - S(80)), root, face, rgba(MUTED, 200), S(3))
    return layer


# ------------------------------------------------------------------ stills
def bloom(dots, size, tight=0.12, wide=0.04, k=1.4) -> tuple[Image.Image, Image.Image]:
    w, h = size
    pitch_guess = max(2, min(w, h) // 90)
    halo_t = dots.filter(ImageFilter.GaussianBlur(pitch_guess * 1.2))
    halo_w = dots.filter(ImageFilter.GaussianBlur(pitch_guess * 3.2))
    def tinted(halo, alpha):
        t = Image.new("RGBA", size, rgba(MINT, 0))
        t.putalpha(halo.getchannel("A").point(lambda v: int(v * alpha)))
        return t
    return tinted(halo_t, tight * 255 * 2), tinted(halo_w, wide * 255 * 2)


def compose(variant: str) -> Image.Image:
    image = Image.new("RGBA", (W, H), rgba(INK, 255))

    if variant == "quiet":
        lum = luminance_crop((0, 0, portrait.PORTRAIT_BOX[2] - portrait.PORTRAIT_BOX[0],
                              int((portrait.PORTRAIT_BOX[3] - portrait.PORTRAIT_BOX[1]) * 0.62)))
        dots = dots_layer((W, H), (240, 560, 800, 1000), 100, lum=lum, color=MUTED)
    else:
        jitter = 16 if variant == "storm" else 0
        rate = 0.03 if variant == "storm" else 0.0
        dots = dots_layer((W, H), (180, 280, 1400, 1600), 200, seed=7,
                          jitter_px=jitter, jitter_rate=rate)

    tight, wide = bloom(dots, (W, H))
    image.alpha_composite(tight)
    image.alpha_composite(wide)
    image.alpha_composite(dots)

    if variant == "storm":
        d = ImageDraw.Draw(image)
        # two frozen glitch lines at eye and chin level, plus one arc to the type
        d.rectangle((180, 660, 1580, 662), fill=rgba(ROSE, 102))
        d.rectangle((180, 1560, 1580, 1562), fill=rgba(ROSE, 102))
        d.arc((900, 480, 3000, 1900), 200, 262, fill=rgba(ROSE, 20), width=2)

    image.alpha_composite(type_block((W, H), quiet=(variant == "quiet"),
                                     storm=(variant == "storm")))

    if variant != "quiet":
        image.alpha_composite(edge_columns((W, H)))
        image.alpha_composite(grain((W, H)))
    image.alpha_composite(scanlines((W, H)))
    image.alpha_composite(vignette((W, H)))
    return image.convert("RGB")


def lock_art() -> Image.Image:
    size = 1024
    image = Image.new("RGBA", (size, size), rgba(INK, 255))
    lum = luminance_crop((0, 0, portrait.PORTRAIT_BOX[2] - portrait.PORTRAIT_BOX[0],
                          int((portrait.PORTRAIT_BOX[3] - portrait.PORTRAIT_BOX[1]) * 0.60)))
    dots = dots_layer((size, size), (312, 90, 400, 500), 96, lum=lum)
    tight, wide = bloom(dots, (size, size))
    image.alpha_composite(tight)
    image.alpha_composite(wide)
    image.alpha_composite(dots)

    d = ImageDraw.Draw(image)
    tracked(d, (352, 646), "0x", font(46, True), rgba(ROSE, 255), 1)
    tracked(d, (410, 646), "PRIVACY", font(46, True), rgba(PHOSPHOR, 255), 8)
    tracked(d, (356, 716), "NO LOGS . NO TRACE . NO NAME", font(17), rgba(FG, 225), 4)
    image.alpha_composite(scanlines((size, size), 3, 6))
    image.alpha_composite(vignette((size, size), 30))
    return image.convert("RGB")


# ------------------------------------------------------------------ saver
def saver_frame(t, base, dots, halos, size, region) -> Image.Image:
    w, h = size
    image = base.copy()
    phase = t * TAU

    # 6.1 travelling dissolve wave: per-strip alpha multiplier, periodic in t
    strip_w = 16
    x0 = region[0] - strip_w
    x1 = region[0] + region[2] + strip_w
    for sx in range(x0, x1, strip_w):
        mod = 0.7 + 0.3 * math.sin((sx / w) * TAU - phase)
        if mod >= 0.999:
            piece = dots.crop((sx, 0, sx + strip_w, h))
            image.alpha_composite(piece, (sx, 0))
            continue
        piece = dots.crop((sx, 0, sx + strip_w, h))
        piece.putalpha(piece.getchannel("A").point(lambda v, m=mod: int(v * m)))
        image.alpha_composite(piece, (sx, 0))

    # 6.3 breathing bloom, phase-offset so it expands as the wave contracts
    for halo, base_a, amp, off in zip(halos, (0.20, 0.07), (0.07, 0.035), (0.0, math.pi / 2)):
        a = base_a + amp * math.sin(phase + off)
        layer = halo.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v, a=a: int(v * min(1.0, max(0.0, a) / 0.3))))
        image.alpha_composite(layer)

    # 6.2 scanline sweep band crossing the portrait, full travel per loop
    band = 64
    y = (t * (h + band)) - band
    d = ImageDraw.Draw(image)
    d.rectangle((region[0], y, region[0] + region[2], y + band), fill=rgba(MINT, 14))
    d.line((region[0], y + band, region[0] + region[2], y + band), fill=rgba(MINT, 72), width=2)
    return image.convert("RGB")


def build_saver(encode=True) -> Image.Image:
    region = (90, 140, 700, 800)
    dots = dots_layer((SW, SH), region, 150)
    halo_t, halo_w = bloom(dots, (SW, SH), 0.3, 0.1)

    base = Image.new("RGBA", (SW, SH), rgba(INK, 255))
    base.alpha_composite(type_block((SW, SH), scale=0.5))
    base.alpha_composite(edge_columns((SW, SH)))
    base.alpha_composite(grain((SW, SH)))
    base.alpha_composite(scanlines((SW, SH)))

    poster = saver_frame(0.0, base, dots, (halo_t, halo_w), (SW, SH), region)
    poster.save(SAVER / "mark.png", optimize=True)
    if not encode:
        return poster

    out = SAVER / "hermes-dots.mp4"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}",
           "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
           "-pix_fmt", "yuv420p", "-g", "24", "-movflags", "+faststart",
           "-metadata", "title=0xHermes v4 - Dot Matrix", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(FRAMES):
            proc.stdin.write(saver_frame(i / FRAMES, base, dots,
                                         (halo_t, halo_w), (SW, SH), region).tobytes())
            if i % 36 == 0:
                print(f"  saver {i:03d}/{FRAMES}", flush=True)
    except BrokenPipeError:
        pass
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"  wrote {out.name} ({out.stat().st_size // 1024} KiB)")
    return poster


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", action="store_true")
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    if not (args.video or args.stills):
        args.stills = True

    if args.stills:
        compose("hero").save(BACKGROUNDS / "20-dot-matrix-hero.png", optimize=True)
        print("  wrote 20-dot-matrix-hero.png")
        compose("quiet").save(BACKGROUNDS / "21-quiet-channel.png", optimize=True)
        print("  wrote 21-quiet-channel.png")
        compose("storm").save(BACKGROUNDS / "22-cipher-storm.png", optimize=True)
        print("  wrote 22-cipher-storm.png")
        lock = lock_art()
        lock.save(ROOT / "unlock.png", optimize=True)
        lock.save(ROOT / "preview-unlock.png", optimize=True)
        ImageOps.fit(compose("hero"), (2560, 1440),
                     method=Image.Resampling.LANCZOS,
                     centering=(0.5, 0.5)).save(ROOT / "preview.png", optimize=True)
        print("  wrote unlock.png + preview.png")
    if args.video:
        build_saver(encode=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
