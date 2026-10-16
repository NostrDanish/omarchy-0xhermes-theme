#!/usr/bin/env python3
"""0xHermes screensaver fallback when mpv is unavailable.

Places the theme mark once, then moves a rose scan across it. One image,
not a reel. Any key exits. Stays at or below 12 FPS.
"""
from __future__ import annotations

import base64
import fcntl
import os
import select
import struct
import sys
import termios
import time
import tty

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = os.path.join(HERE, "mark.png")
FPS = min(12.0, float(os.environ.get("OMARCHY_SAVER_FPS", "8") or 8))
NEON = "\033[38;2;57;255;20m"
ROSE = "\033[38;2;255;46;99m"
DIM = "\033[38;2;46;92;58m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"
ALT_ON = "\033[?1049h"
ALT_OFF = "\033[?1049l"
CLEAR = "\033[2J\033[H"


def key_waiting() -> bool:
    return bool(select.select([sys.stdin], [], [], 0)[0])


def winsize() -> tuple[int, int, int, int]:
    packed = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
    rows, cols, xpix, ypix = struct.unpack("HHHH", packed)
    return rows or 40, cols or 120, xpix, ypix


def kitty_image(png: bytes, cols: int, rows: int) -> None:
    payload = base64.standard_b64encode(png).decode("ascii")
    chunk = 4096
    first = True
    while payload:
        piece, payload = payload[:chunk], payload[chunk:]
        more = 1 if payload else 0
        if first:
            header = f"a=T,f=100,q=2,C=1,c={cols},r={rows},m={more}"
            first = False
        else:
            header = f"m={more}"
        sys.stdout.write(f"\033_G{header};{piece}\033\\")
    sys.stdout.flush()


def text_frame(cols: int, rows: int, scan: int) -> str:
    lines = [" " * cols for _ in range(rows)]
    title = "0xPRIVACY"
    x = max(0, (cols - len(title)) // 2)
    y = max(1, rows // 2 - 1)
    row = list(lines[y])
    for i, ch in enumerate(title):
        if x + i < cols:
            row[x + i] = ch
    lines[y] = "".join(row)
    if 0 <= scan < rows:
        lines[scan] = ("─" * cols)
    foot = "YOUR KEYS  ·  YOUR DATA  ·  YOUR FREEDOM"
    fy = rows - 2
    fx = max(0, (cols - len(foot)) // 2)
    row = list(lines[fy])
    for i, ch in enumerate(foot):
        if fx + i < cols:
            row[fx + i] = ch
    lines[fy] = "".join(row)
    return "\n".join(lines)


def main() -> int:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd) if sys.stdin.isatty() else None
    if old is not None:
        tty.setcbreak(fd)
    sys.stdout.write(ALT_ON + HIDE + CLEAR + "\033]11;rgb:02/08/04\007")
    sys.stdout.flush()
    rows, cols, _, _ = winsize()
    png = open(MARK, "rb").read() if os.path.isfile(MARK) else b""
    if png:
        try:
            kitty_image(png, cols, rows)
        except OSError:
            png = b""
    scan = 0
    target = 1.0 / max(6.0, FPS)
    try:
        while True:
            if sys.stdin.isatty() and key_waiting():
                os.read(fd, 64)
                break
            rows, cols, _, _ = winsize()
            sys.stdout.write("\033[H")
            frame = text_frame(cols, rows, scan)
            colored = []
            for i, line in enumerate(frame.splitlines()):
                if i == scan:
                    colored.append(ROSE + line + RESET)
                elif "0xPRIVACY" in line:
                    colored.append(NEON + line + RESET)
                else:
                    colored.append(DIM + line + RESET)
            sys.stdout.write("\n".join(colored))
            sys.stdout.flush()
            scan = (scan + 1) % max(1, rows)
            if sys.stdin.isatty() and select.select([sys.stdin], [], [], target)[0]:
                os.read(fd, 64)
                break
            if not sys.stdin.isatty():
                time.sleep(target)
    finally:
        sys.stdout.write("\033_Ga=d,q=2\033\\" + SHOW + RESET + ALT_OFF)
        sys.stdout.flush()
        if old is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
