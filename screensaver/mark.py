#!/usr/bin/env python3
"""Low-cost 0xHermes v2 screensaver fallback when mpv is unavailable.

Display one poster frame (Kitty graphics protocol when available), then poll
for input at no more than 12 Hz. Any key exits; no full-screen redraw loop.
"""
from __future__ import annotations

import base64
import fcntl
import os
import select
import struct
import sys
import termios
import tty

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = os.path.join(HERE, "mark.png")

try:
    FPS = min(12.0, max(1.0, float(os.environ.get("OMARCHY_SAVER_FPS", "12") or 12)))
except ValueError:
    FPS = 12.0

PHOSPHOR = "\033[38;2;57;255;20m"
ROSE = "\033[38;2;255;46;99m"
DIM = "\033[38;2;66;107;75m"
RESET = "\033[0m"
HIDE = "\033[?25l"
SHOW = "\033[?25h"
ALT_ON = "\033[?1049h"
ALT_OFF = "\033[?1049l"
CLEAR = "\033[2J\033[H"


def winsize() -> tuple[int, int, int, int]:
    try:
        packed = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
        rows, cols, xpix, ypix = struct.unpack("HHHH", packed)
        return rows or 40, cols or 120, xpix, ypix
    except OSError:
        return 40, 120, 0, 0


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


def text_fallback(cols: int, rows: int) -> None:
    title = "0xHERMES"
    tagline = "SIGNAL / PRIVATE / LOCAL"
    y = max(2, rows // 2)
    x = max(0, (cols - len(title)) // 2)
    tx = max(0, (cols - len(tagline)) // 2)
    sys.stdout.write(f"\033[{y};{x + 1}H{ROSE}0x{PHOSPHOR}HERMES{RESET}")
    sys.stdout.write(f"\033[{min(rows - 1, y + 2)};{tx + 1}H{DIM}{tagline}{RESET}")
    sys.stdout.flush()


def main() -> int:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd) if sys.stdin.isatty() else None
    if old is not None:
        tty.setcbreak(fd)

    rows, cols, _, _ = winsize()
    png = open(MARK, "rb").read() if os.path.isfile(MARK) else b""
    sys.stdout.write(ALT_ON + HIDE + CLEAR + "\033]11;rgb:02/08/04\007")
    sys.stdout.flush()

    try:
        if png:
            try:
                kitty_image(png, cols, rows)
            except OSError:
                png = b""
        if not png:
            text_fallback(cols, rows)

        interval = 1.0 / FPS
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], interval)
            if ready:
                os.read(fd, 64)
                break
    finally:
        sys.stdout.write("\033_Ga=d,q=2\033\\" + SHOW + RESET + ALT_OFF)
        sys.stdout.flush()
        if old is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
