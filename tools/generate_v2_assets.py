#!/usr/bin/env python3
"""Build original 0xHermes v2 artwork with Pillow and FFmpeg.

No downloaded artwork or runtime network access. The wallpaper is native
5120x2160; the saver is a native 2560x1080, 30 FPS seamless loop.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BACKGROUNDS = ROOT / "backgrounds"
SAVER = ROOT / "screensaver"
FONT_REGULAR = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf"

INK = "#050A08"
DEEP = "#020504"
PHOSPHOR = "#72F1A5"
PHOSPHOR_BRIGHT = "#B9FFD2"
ROSE = "#FF5C8A"
FOREGROUND = "#D9F3E3"
MUTED = "#769783"
GRID = "#234534"
TAU = math.tau


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def tracked_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    face: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int] | str,
    tracking: float = 0,
) -> float:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=face, fill=fill)
        x += draw.textlength(char, font=face) + tracking
    return x


def base_field(width: int, height: int, rose: bool = False) -> Image.Image:
    """Smooth, dither-free ambient light rendered from a small color field."""
    sw, sh = 640, max(128, round(640 * height / width))
    field = Image.new("RGB", (sw, sh))
    px = field.load()
    for y in range(sh):
        ny = y / max(1, sh - 1)
        for x in range(sw):
            nx = x / max(1, sw - 1)
            dg = ((nx - 0.73) / 0.46) ** 2 + ((ny - 0.45) / 0.72) ** 2
            dr = ((nx - 0.08) / 0.42) ** 2 + ((ny - 0.88) / 0.60) ** 2
            green = math.exp(-3.2 * dg)
            pink = math.exp(-3.6 * dr)
            if rose:
                green, pink = pink * 0.65, green * 1.3
            edge = max(0.0, (abs(nx - 0.5) * 1.55) ** 2 + (abs(ny - 0.5) * 1.35) ** 2)
            r = 4 + 8 * pink + 1 * green - 2 * edge
            g = 9 + 18 * green + 1.5 * pink - 4 * edge
            b = 7 + 10 * green + 8 * pink - 3 * edge
            px[x, y] = (max(1, int(r)), max(2, int(g)), max(2, int(b)))
    return field.resize((width, height), Image.Resampling.BICUBIC).convert("RGBA")


def add_grid(image: Image.Image, spacing: int, alpha: int = 15) -> None:
    w, h = image.size
    grid = Image.new("RGBA", image.size)
    d = ImageDraw.Draw(grid)
    for x in range(0, w, spacing):
        major = (x // spacing) % 4 == 0
        d.line((x, 0, x, h), fill=rgba(GRID, alpha + (5 if major else 0)), width=1)
    for y in range(0, h, spacing):
        major = (y // spacing) % 4 == 0
        d.line((0, y, w, y), fill=rgba(GRID, alpha + (5 if major else 0)), width=1)
    image.alpha_composite(grid)


def dashed_arc(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    start: float,
    end: float,
    fill: tuple[int, int, int, int],
    width: int,
    dash: float = 8,
    gap: float = 7,
) -> None:
    angle = start
    while angle < end:
        draw.arc(box, angle, min(angle + dash, end), fill=fill, width=width)
        angle += dash + gap


def hermes_mark(size: int, bright: bool = False) -> Image.Image:
    """An abstract winged H: messenger wings around a private signal core."""
    scale = size / 800
    layer = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(layer)
    cx = cy = size / 2
    green = rgba(PHOSPHOR_BRIGHT if bright else PHOSPHOR, 225)
    dim = rgba(PHOSPHOR, 72)
    pink = rgba(ROSE, 230)

    for radius, a, start, end in (
        (350, 58, 198, 342),
        (350, 58, 18, 162),
        (302, 38, 210, 330),
        (302, 38, 30, 150),
    ):
        r = radius * scale
        dashed_arc(d, (cx - r, cy - r, cx + r, cy + r), start, end, rgba(PHOSPHOR, a), max(1, round(2 * scale)), 5, 5)

    # Reticle ticks and a split hexagonal containment field.
    for i in range(48):
        a = TAU * i / 48
        r1 = 326 * scale
        r2 = (336 if i % 4 == 0 else 331) * scale
        d.line(
            (cx + math.cos(a) * r1, cy + math.sin(a) * r1, cx + math.cos(a) * r2, cy + math.sin(a) * r2),
            fill=rgba(PHOSPHOR, 72 if i % 4 == 0 else 32),
            width=max(1, round(2 * scale)),
        )
    hexagon = [(cx + math.cos(TAU * i / 6 - math.pi / 2) * 235 * scale, cy + math.sin(TAU * i / 6 - math.pi / 2) * 235 * scale) for i in range(6)]
    d.line(hexagon + [hexagon[0]], fill=rgba(PHOSPHOR, 50), width=max(1, round(2 * scale)), joint="curve")

    # Wing feathers: ascending, open, and deliberately asymmetric in color.
    for side in (-1, 1):
        for i in range(3):
            y = cy + (-96 + i * 70) * scale
            points = [
                (cx + side * 72 * scale, y + 34 * scale),
                (cx + side * (174 + i * 17) * scale, y - (42 - i * 9) * scale),
                (cx + side * (262 + i * 11) * scale, y - (24 - i * 7) * scale),
            ]
            d.line(points, fill=green if side == 1 else rgba(PHOSPHOR, 180), width=max(2, round((7 - i) * scale)), joint="curve")
        d.line(
            (cx + side * 83 * scale, cy - 142 * scale, cx + side * 83 * scale, cy + 155 * scale),
            fill=green,
            width=max(2, round(8 * scale)),
        )

    d.line((cx - 82 * scale, cy + 4 * scale, cx + 82 * scale, cy + 4 * scale), fill=green, width=max(2, round(8 * scale)))
    d.line((cx, cy - 168 * scale, cx, cy + 168 * scale), fill=rgba(PHOSPHOR_BRIGHT, 105), width=max(1, round(2 * scale)))
    r = 18 * scale
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba(DEEP, 255), outline=pink, width=max(2, round(5 * scale)))
    r = 4 * scale
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=pink)

    # Tiny signal nodes keep the emblem technical without binary-rain clichés.
    for x, y, color in ((-272, -122, green), (294, 88, pink), (-218, 175, dim), (218, -175, dim)):
        rr = 5 * scale
        px, py = cx + x * scale, cy + y * scale
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=color)
    return layer


def add_orbits(image: Image.Image, center: tuple[float, float], scale: float, rose: bool = False) -> None:
    w, h = image.size
    cx, cy = center
    layer = Image.new("RGBA", image.size)
    d = ImageDraw.Draw(layer)
    for i in range(8):
        rx = (330 + i * 122) * scale
        ry = rx * 0.55
        start = (i * 37 + 12) % 360
        color = ROSE if rose and i % 3 == 0 else PHOSPHOR
        alpha = max(15, 58 - i * 5)
        d.arc((cx - rx, cy - ry, cx + rx, cy + ry), start, start + 205, fill=rgba(color, alpha), width=max(1, round(2 * scale)))
        if i % 2 == 0:
            dashed_arc(d, (cx - rx, cy - ry, cx + rx, cy + ry), start + 216, start + 342, rgba(color, alpha // 2), max(1, round(2 * scale)), 4, 7)
    # Long rails imply motion and connect the composition across an ultrawide.
    d.line((0, h * 0.84, cx - 280 * scale, cy + 130 * scale), fill=rgba(PHOSPHOR, 25), width=max(1, round(scale)))
    d.line((w, h * 0.12, cx + 250 * scale, cy - 100 * scale), fill=rgba(ROSE, 27), width=max(1, round(scale)))
    image.alpha_composite(layer)


def add_particles(image: Image.Image, center: tuple[float, float], scale: float, seed: int = 20) -> None:
    rnd = random.Random(seed)
    layer = Image.new("RGBA", image.size)
    d = ImageDraw.Draw(layer)
    cx, cy = center
    for i in range(115):
        angle = rnd.random() * TAU
        radius = rnd.uniform(260, 1180) * scale
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius * 0.47
        if not (0 <= x < image.width and 0 <= y < image.height):
            continue
        rr = rnd.choice((1, 1, 2, 2, 3)) * scale
        color = ROSE if i % 13 == 0 else PHOSPHOR
        alpha = rnd.randint(28, 100)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=rgba(color, alpha))
    image.alpha_composite(layer)


def add_scanlines(image: Image.Image, period: int = 5, alpha: int = 5) -> None:
    scan = Image.new("RGBA", image.size)
    d = ImageDraw.Draw(scan)
    for y in range(0, image.height, period):
        d.line((0, y, image.width, y), fill=(0, 0, 0, alpha), width=1)
    image.alpha_composite(scan)


def wallpaper(name: str, variant: str) -> Image.Image:
    w, h = 5120, 2160
    rose = variant == "rose"
    image = base_field(w, h, rose=rose)
    add_grid(image, 128, 12 if variant == "ghost" else 15)
    center = (w * 0.72, h * 0.46)
    add_orbits(image, center, 1.45, rose=rose)
    add_particles(image, center, 1.25, seed=29 if rose else 20)

    if variant != "ghost":
        mark = hermes_mark(900, bright=True)
        glow = Image.new("RGBA", image.size)
        gd = ImageDraw.Draw(glow)
        gd.ellipse((center[0] - 360, center[1] - 360, center[0] + 360, center[1] + 360), fill=rgba(ROSE if rose else PHOSPHOR, 32))
        glow = glow.filter(ImageFilter.GaussianBlur(120))
        image.alpha_composite(glow)
        image.alpha_composite(mark, (round(center[0] - 450), round(center[1] - 450)))

    if variant in {"hero", "rose"}:
        d = ImageDraw.Draw(image)
        x, y = 240, 1240
        tracked_text(d, (x, y), "PRIVATE INTELLIGENCE / 02", font(27), rgba(MUTED, 230), 5)
        tracked_text(d, (x - 4, y + 80), "0x", font(108, True), rgba(ROSE, 255), 2)
        tracked_text(d, (x + 166, y + 32), "HERMES", font(142, True), rgba(FOREGROUND, 255), 7)
        d.line((x, y + 235, x + 1000, y + 235), fill=rgba(PHOSPHOR, 90), width=2)
        tracked_text(d, (x, y + 278), "LOCAL BY DEFAULT.  ZERO NOISE.", font(30), rgba(PHOSPHOR, 215), 3)
        tracked_text(d, (x, h - 160), "SIGNAL TEMPLE  /  OMARCHY EDITION", font(22), rgba(MUTED, 170), 3)
        tracked_text(d, (w - 680, h - 160), "51°08′N  //  NODE: DESKTOP", font(20), rgba(MUTED, 135), 2)
    elif variant == "channel":
        d = ImageDraw.Draw(image)
        tracked_text(d, (240, h - 175), "OPEN CHANNEL / CLOSED LOOP", font(25), rgba(MUTED, 180), 4)
    else:
        d = ImageDraw.Draw(image)
        tracked_text(d, (240, h - 175), "0xHERMES  /  GHOST GRID", font(22), rgba(MUTED, 125), 4)

    add_scanlines(image)
    # Dark top and bottom shelves improve bar and window legibility.
    shelves = Image.new("RGBA", image.size)
    sd = ImageDraw.Draw(shelves)
    for i in range(180):
        a = round(60 * (1 - i / 180) ** 2)
        sd.line((0, i, w, i), fill=(0, 3, 2, a))
        sd.line((0, h - 1 - i, w, h - 1 - i), fill=(0, 3, 2, a))
    image.alpha_composite(shelves)
    output = BACKGROUNDS / name
    image.convert("RGB").save(output, optimize=True)
    return image


def lock_and_previews(hero: Image.Image) -> None:
    size = 1024
    lock = base_field(size, size)
    add_grid(lock, 64, 13)
    add_orbits(lock, (size * 0.5, size * 0.40), 0.56)
    lock.alpha_composite(hermes_mark(500, bright=True), (262, 90))
    d = ImageDraw.Draw(lock)
    title = "0xHERMES"
    face = font(65, True)
    tw = d.textlength(title, font=face)
    d.text(((size - tw) / 2, 675), title, font=face, fill=FOREGROUND)
    tracked_text(d, (254, 770), "PRIVATE INTELLIGENCE", font(18), rgba(PHOSPHOR, 210), 3)
    d.line((362, 820, 662, 820), fill=rgba(ROSE, 150), width=2)
    tracked_text(d, (402, 850), "V2 / LOCAL", font(15), rgba(MUTED, 180), 2)
    add_scanlines(lock, 4, 6)
    lock.convert("RGB").save(ROOT / "unlock.png", optimize=True)
    lock.convert("RGB").save(ROOT / "preview-unlock.png", optimize=True)
    preview = ImageOps.fit(hero.convert("RGB"), (2560, 1440), method=Image.Resampling.LANCZOS, centering=(0.58, 0.5))
    preview.save(ROOT / "preview.png", optimize=True)


def saver_base() -> Image.Image:
    base = base_field(2560, 1080)
    add_grid(base, 96, 11)
    # Static shelves frame the moving signal without bright burn-in strips.
    d = ImageDraw.Draw(base)
    tracked_text(d, (72, 56), "0x / IDLE CHANNEL", font(18), rgba(MUTED, 125), 3)
    tracked_text(d, (2010, 980), "PRIVATE / LOCAL / YOURS", font(17), rgba(MUTED, 115), 2)
    add_scanlines(base, 5, 5)
    return base


def saver_frame(
    index: int,
    frames: int,
    base: Image.Image,
    outer: Image.Image,
    core: Image.Image,
    label: Image.Image,
) -> Image.Image:
    t = index / frames
    phase = TAU * t
    image = base.copy()
    cx = 1280 + 150 * math.sin(phase)
    cy = 462 + 48 * math.sin(phase * 2)

    glow = Image.new("RGBA", image.size)
    gd = ImageDraw.Draw(glow)
    pulse = 24 + round(9 * (1 + math.sin(phase * 2)))
    gd.ellipse((cx - 330, cy - 330, cx + 330, cy + 330), fill=rgba(PHOSPHOR, pulse))
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(95)))

    rotated = outer.rotate(-360 * t, resample=Image.Resampling.BICUBIC, expand=False)
    image.alpha_composite(rotated, (round(cx - outer.width / 2), round(cy - outer.height / 2)))
    image.alpha_composite(core, (round(cx - core.width / 2), round(cy - core.height / 2)))
    image.alpha_composite(label, (round(cx - label.width / 2), round(cy + 342)))

    # Packet lights follow closed orbital paths, so the loop has no reset frame.
    particles = Image.new("RGBA", image.size)
    pd = ImageDraw.Draw(particles)
    for i in range(28):
        a = phase * (1 if i % 2 else -1) + TAU * i / 28
        radius = 310 + (i % 4) * 58
        x = cx + math.cos(a) * radius
        y = cy + math.sin(a) * radius * 0.58
        rr = 2 if i % 5 else 3
        color = ROSE if i % 7 == 0 else PHOSPHOR
        pd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=rgba(color, 120 if i % 5 else 210))

    # The scanner is fully off-canvas at both sides of the loop boundary.
    scan_x = -500 + (image.width + 1000) * t
    pd.polygon(((scan_x - 90, 0), (scan_x + 20, 0), (scan_x + 280, image.height), (scan_x + 170, image.height)), fill=rgba(PHOSPHOR, 8))
    pd.line((scan_x + 20, 0, scan_x + 280, image.height), fill=rgba(ROSE, 32), width=2)
    image.alpha_composite(particles)
    return image.convert("RGB")


def saver_still() -> None:
    base = saver_base()
    outer = hermes_mark(880)
    core = hermes_mark(590, bright=True)
    label = Image.new("RGBA", (760, 160))
    d = ImageDraw.Draw(label)
    tracked_text(d, (108, 0), "0xHERMES", font(60, True), rgba(FOREGROUND, 240), 5)
    tracked_text(d, (130, 86), "SIGNAL / PRIVATE / LOCAL", font(18), rgba(PHOSPHOR, 175), 3)
    frame = saver_frame(0, 360, base, outer, core, label)
    frame.save(SAVER / "preview.png", optimize=True)
    frame.save(SAVER / "mark.png", optimize=True)


def render_saver() -> None:
    width, height, fps, seconds = 2560, 1080, 30, 12
    frames = fps * seconds
    base = saver_base()
    outer = hermes_mark(880)
    core = hermes_mark(590, bright=True)
    label = Image.new("RGBA", (760, 160))
    d = ImageDraw.Draw(label)
    tracked_text(d, (108, 0), "0xHERMES", font(60, True), rgba(FOREGROUND, 240), 5)
    tracked_text(d, (130, 86), "SIGNAL / PRIVATE / LOCAL", font(18), rgba(PHOSPHOR, 175), 3)
    output = SAVER / "hermes-v2.mp4"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
        "-g", "60", "-movflags", "+faststart", "-metadata", "title=0xHermes V2 - Signal Temple", str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for i in range(frames):
            frame = saver_frame(i, frames, base, outer, core, label)
            process.stdin.write(frame.tobytes())
            if i % 30 == 0:
                print(f"rendered {i:03d}/{frames}", flush=True)
    except BrokenPipeError:
        pass
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("ffmpeg failed to encode the v2 screensaver")
    print(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stills", action="store_true", help="build wallpapers, lock image, and saver poster")
    parser.add_argument("--video", action="store_true", help="render the 30 FPS saver")
    args = parser.parse_args()
    if not args.stills and not args.video:
        args.stills = True
    BACKGROUNDS.mkdir(parents=True, exist_ok=True)
    SAVER.mkdir(parents=True, exist_ok=True)
    if args.stills:
        hero = wallpaper("00-signal-temple.png", "hero")
        wallpaper("01-open-channel.png", "channel")
        wallpaper("02-ghost-grid.png", "ghost")
        wallpaper("03-rose-protocol.png", "rose")
        lock_and_previews(hero)
        saver_still()
        print("Built four 5120x2160 wallpapers, lock artwork, and saver poster.")
    if args.video:
        render_saver()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
