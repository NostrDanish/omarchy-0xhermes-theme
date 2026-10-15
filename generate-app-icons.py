#!/usr/bin/python3
"""Generate monochrome phosphor-green app icons for visible desktop launchers."""
from __future__ import annotations

import configparser
import glob
import io
import os
import re
import shutil
import subprocess
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, Gtk
from PIL import Image, ImageDraw, ImageFont

HOME = Path.home()
THEME_NAME = "0xPrivacy-Phosphor"
ICON_ROOT = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share")) / "icons" / THEME_NAME
APP_ICON_DIR = ICON_ROOT / "256x256" / "apps"
BACKUP_SUFFIX = ".0xprivacy-original"
# The FLUID desktop file uses "fluid", while its package ships "fluid1.3".
ALIASES = {"fluid": "fluid1.3"}
PHOSPHOR = (57, 255, 20, 255)


def desktop_entries() -> list[Path]:
    roots = [Path("/usr/share/applications"), HOME / ".local/share/applications"]
    entries: set[Path] = set()
    for root in roots:
        if root.is_dir():
            entries.update(Path(p) for p in glob.glob(str(root / "*.desktop")))
    return sorted(entries, key=str)


def parse_entry(text: str, path: Path) -> tuple[str, str] | None:
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    try:
        parser.read_string(text)
        section = parser["Desktop Entry"]
    except (configparser.Error, KeyError):
        return None
    if section.get("NoDisplay", "false").lower() == "true" or section.get("Hidden", "false").lower() == "true":
        return None
    icon = section.get("Icon", "").strip()
    if not icon:
        return None
    name = section.get("Name", path.stem)
    return name, icon


def rewrite_icon(text: str, icon_name: str) -> str:
    lines = text.splitlines(keepends=True)
    in_entry = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_entry:
                break
            in_entry = stripped == "[Desktop Entry]"
        elif in_entry and line.startswith("Icon="):
            ending = "\n" if line.endswith("\n") else ""
            lines[index] = f"Icon={icon_name}{ending}"
            return "".join(lines)
    if in_entry:
        insert_at = next((i for i, line in enumerate(lines) if i > 0 and line.strip().startswith("[")), len(lines))
        lines.insert(insert_at, f"Icon={icon_name}\n")
    return "".join(lines)


def icon_source(theme: Gtk.IconTheme, icon: str) -> Path | None:
    direct = Path(icon).expanduser()
    if direct.is_absolute() and direct.is_file():
        return direct
    for candidate in (icon, ALIASES.get(icon, "")):
        if not candidate:
            continue
        info = theme.lookup_icon(candidate, 256, 0)
        if info:
            filename = info.get_filename()
            if filename and Path(filename).is_file():
                return Path(filename)
    return None


def pixbuf_to_image(path: Path) -> Image.Image:
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), 512, 512, True)
    ok, raw = pixbuf.save_to_bufferv("png", [], [])
    if not ok:
        raise RuntimeError(f"Could not decode app icon: {path}")
    image = Image.open(io.BytesIO(raw)).convert("RGBA")
    # Trim transparent padding first, then scale the visible art to menu-icon size.
    bounds = image.getchannel("A").getbbox()
    if bounds:
        image = image.crop(bounds)
    image.thumbnail((224, 224), Image.Resampling.LANCZOS)
    # Replace every source hue with the theme's phosphor green while preserving
    # luminance and alpha, so logos stay legible but no brand colors remain.
    mapped = []
    raw_pixels = image.tobytes()
    for offset in range(0, len(raw_pixels), 4):
        red, green, blue, alpha = raw_pixels[offset : offset + 4]
        luminance = (2126 * red + 7152 * green + 722 * blue) / 10000 / 255
        level = int(round(255 * (luminance ** 0.65)))
        # Duotone: darker ink is rose, brighter ink is neon green.
        color = (255, 46, 99) if luminance < 0.42 else (57, 255, 20)
        mapped.append((round(color[0] * level / 255), round(color[1] * level / 255), round(color[2] * level / 255), alpha))
    image.putdata(mapped)
    return image


def draw_missing_symbol(name: str, icon: str, box: int = 224) -> Image.Image:
    image = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if icon == "hwloc":
        # A processor/topology graph for lstopo (Hardware Locality).
        points = [
            (box * 0.50, box * 0.15),
            (box * 0.29, box * 0.49),
            (box * 0.71, box * 0.49),
            (box * 0.16, box * 0.82),
            (box * 0.38, box * 0.82),
            (box * 0.62, box * 0.82),
            (box * 0.84, box * 0.82),
        ]
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        width = max(4, round(box * 0.035))
        radius = max(8, round(box * 0.065))
        for a, b in edges:
            draw.line((points[a], points[b]), fill=PHOSPHOR, width=width)
        for x, y in points:
            draw.rounded_rectangle((x - radius, y - radius, x + radius, y + radius),
                                   radius=max(3, round(radius * 0.3)),
                                   fill=(0, 0, 0, 0), outline=PHOSPHOR, width=width)
    else:
        letters = "".join(part[0] for part in re.findall(r"[A-Za-z0-9]+", name)[:2]).upper() or "APP"
        draw.ellipse((box * 0.08, box * 0.08, box * 0.92, box * 0.92),
                     fill=(0, 0, 0, 0), outline=PHOSPHOR, width=max(4, round(box * 0.03)))
        font = ImageFont.load_default()
        bounds = draw.textbbox((0, 0), letters, font=font)
        draw.text(((box - (bounds[2] - bounds[0])) / 2, (box - (bounds[3] - bounds[1])) / 2),
                  letters, font=font, fill=PHOSPHOR)
    return image


def make_cover(source: Path | None, app_name: str, icon: str) -> Image.Image:
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    if source is not None:
        logo = pixbuf_to_image(source)
    else:
        logo = draw_missing_symbol(app_name, icon)
    x = (256 - logo.width) // 2
    y = (256 - logo.height) // 2
    canvas.alpha_composite(logo, (x, y))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((10, 10, 245, 245), radius=28, outline=PHOSPHOR, width=4)
    draw.rectangle((18, 18, 46, 238), fill=(255, 46, 99, 255))
    return canvas


def main() -> None:
    Gtk.init([])
    base_theme = Gtk.IconTheme.new()
    base_theme.set_custom_theme("Yaru-olive-dark")
    APP_ICON_DIR.mkdir(parents=True, exist_ok=True)

    # Map original icon declarations to stable identifiers. For per-user web app
    # launchers that use absolute icon paths, preserve the original entry once and
    # switch only its Icon= field to the new theme icon.
    sources: dict[str, tuple[str, Path | None, str]] = {}
    visible_entries = 0
    local_rewrites = 0
    unresolved: list[tuple[str, str]] = []
    root = (HOME / ".local/share/applications").resolve()

    for path in desktop_entries():
        current_text = path.read_text(encoding="utf-8", errors="replace")
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        source_text = backup.read_text(encoding="utf-8", errors="replace") if backup.exists() else current_text
        parsed = parse_entry(source_text, path)
        if parsed is None:
            continue
        app_name, original_icon = parsed
        visible_entries += 1
        original_path = Path(original_icon).expanduser()
        is_absolute = original_path.is_absolute()
        if is_absolute:
            icon_name = "0xprivacy-" + re.sub(r"[^A-Za-z0-9._-]+", "-", original_path.stem)
            source = original_path if original_path.is_file() else None
            if path.resolve().parent == root:
                if not backup.exists():
                    backup.write_text(current_text, encoding="utf-8")
                rewritten = rewrite_icon(current_text, icon_name)
                if rewritten != current_text:
                    path.write_text(rewritten, encoding="utf-8")
                    local_rewrites += 1
            else:
                unresolved.append((app_name, f"absolute icon cannot be overridden safely: {original_icon}"))
        else:
            icon_name = original_icon
            source = icon_source(base_theme, original_icon)

        if icon_name not in sources:
            sources[icon_name] = (app_name, source, original_icon)
        elif sources[icon_name][1] is None and source is not None:
            sources[icon_name] = (app_name, source, original_icon)

    generated = 0
    for icon_name, (app_name, source, original_icon) in sources.items():
        if source is None:
            unresolved.append((app_name, original_icon))
        output = APP_ICON_DIR / f"{icon_name}.png"
        make_cover(source, app_name, original_icon).save(output, format="PNG", optimize=True)
        generated += 1

    (ICON_ROOT / "index.theme").write_text(
        "[Icon Theme]\n"
        f"Name={THEME_NAME}\n"
        "Comment=0xPrivacy monochrome phosphor-green application covers\n"
        "Inherits=Yaru-olive-dark\n"
        "Directories=256x256/apps\n\n"
        "[256x256/apps]\n"
        "Size=256\n"
        "Type=Fixed\n"
        "Context=Applications\n",
        encoding="utf-8",
    )
    updater = shutil.which("gtk-update-icon-cache")
    if updater:
        subprocess.run([updater, "-f", str(ICON_ROOT)], check=True, stdout=subprocess.DEVNULL)

    print(f"Visible desktop launchers: {visible_entries}")
    print(f"Unique app covers generated: {generated}")
    print(f"User launcher Icon= fields updated: {local_rewrites}")
    if unresolved:
        for app_name, detail in unresolved:
            print(f"FALLBACK COVER: {app_name} ({detail})")
    else:
        print("All visible launchers have a source icon or a generated phosphor fallback.")
    print(f"Icon theme: {ICON_ROOT}")


if __name__ == "__main__":
    main()
