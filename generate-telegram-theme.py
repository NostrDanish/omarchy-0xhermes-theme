#!/usr/bin/python3
"""Build the 0xPrivacy Telegram Desktop theme from Telegram's full current palette."""
from __future__ import annotations

import io
import re
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "telegram"
OUT.mkdir(parents=True, exist_ok=True)

# Use Telegram Desktop's official bundled night-green theme as a complete,
# current schema reference; pin the upstream file commit for reproducibility.
UPSTREAM_COMMIT = "1e66d5874c973b9b573492796cbb641152c03f3c"
UPSTREAM_URL = (
    "https://raw.githubusercontent.com/telegramdesktop/tdesktop/"
    f"{UPSTREAM_COMMIT}/Telegram/Resources/night-green.tdesktop-theme"
)

# 0xPrivacy dark-web roles: neon green, forest-green depth, rose-red signals.
BG = "#020804"
BG_DARK = "#010402"
BG_SURFACE = "#09180e"
BG_HOVER = "#0e2114"
BG_SELECTED = "#12381f"
BG_SELECTED_HI = "#1a4929"
BG_RED = "#3a0c1a"
TEXT = "#c7f5ce"
TEXT_BRIGHT = "#f2fff4"
TEXT_MUTED = "#63856b"
TEXT_DISABLED = "#3d5c44"
ACCENT = "#39ff14"
ACCENT_BRIGHT = "#83ff60"
ACCENT_DEEP = "#15512c"
ACCENT_GREEN = "#2bbf68"
ACCENT_LIME = "#a8ff45"
ACCENT_LIME_BRIGHT = "#c1ff6b"
RED = "#ff2e63"
RED_BRIGHT = "#ff7390"

LINE_RE = re.compile(r"^(\s*)([A-Za-z][A-Za-z0-9_]*)\s*:\s*([^;]+)(;.*)$")

ROOT_BACKGROUNDS = {
    "windowBg", "menuBg", "titleBg", "titleBgActive", "dialogsBg",
    "contactsBg", "introBg", "topBarBg", "emojiPanBg",
    "historyComposeAreaBg", "mediaviewBg", "mediaviewVideoBg", "callBg",
    "mainMenuBg", "sideBarBg", "imageBg", "stickerPreviewBg",
}
DARK_BACKGROUNDS = {"layerBg", "mainMenuCoverBg", "mainMenuCloudBg", "boxSearchBg"}
SURFACE_BACKGROUNDS = {"boxBg", "contactsBgOver", "emojiPanHeaderBg", "filterInputInactiveBg", "filterInputActiveBg", "botKbBg", "botKbDownBg", "mediaviewMenuBg", "mediaviewCaptionBg", "notificationBg", "toastBg", "tooltipBg", "titleButtonBg", "titleButtonBgActive", "titleButtonBgActiveOver", "titleButtonBgOver", "titleButtonCloseBg", "titleButtonCloseBgActive"}
ACCENT_BG_KEYS = {
    "windowBgActive", "activeButtonBg", "activeButtonBgOver", "activeButtonBgRipple",
    "trayCounterBg", "dialogsUnreadBg", "dialogsUnreadBgOver",
    "dialogsUnreadBgActive", "dialogsVerifiedIconBg", "dialogsVerifiedIconBgOver",
    "dialogsVerifiedIconBgActive", "overviewCheckBg", "overviewCheckBgActive",
    "profileVerifiedCheckBg", "historyComposeButtonBg", "historyComposeButtonBgOver",
    "callAnswerBg",
}
DARK_ON_ACCENT_FG = {
    "windowFgActive", "activeButtonFg", "activeButtonFgOver", "activeButtonSecondaryFg",
    "activeButtonSecondaryFgOver", "trayCounterFg", "trayCounterFgMacInvert",
    "dialogsUnreadFg", "dialogsUnreadFgOver", "dialogsUnreadFgActive",
    "dialogsVerifiedIconFg", "dialogsVerifiedIconFgActive", "dialogsOnlineBadgeFg",
    "dialogsOnlineBadgeFgActive", "overviewCheckFg", "overviewCheckFgActive", "historySendIconFg",
 "historySendIconFgOver", "callIconFg",
 }
MUTED_FG_EXACT = {
    "windowSubTextFg", "windowSubTextFgOver", "menuIconFg", "menuSubmenuArrowFg",
    "menuFgDisabled", "menuSeparatorFg", "smallCloseIconFg", "smallCloseIconFgOver",
    "placeholderFg", "inputBorderFg", "filterInputBorderFg", "tooltipBorderFg",
    "boxTitleAdditionalFg", "boxTitleCloseFg", "boxTitleCloseFgOver",
    "membersAboutLimitFg", "contactsStatusFg", "contactsStatusFgOver",
    "dialogsDateFg", "dialogsDateFgOver", "dialogsDateFgActive", "dialogsDraftFg",
    "dialogsDraftFgOver", "dialogsTextFgService", "dialogsTextFgServiceOver",
    "dialogsTextFgServiceActive", "dialogsSendingIconFg", "dialogsSendingIconFgOver",
    "dialogsDateFgActive", "searchedBarFg", "emojiPanHeaderFg", "historyUnreadBarFg",
    "historyComposeAreaFgService",
    "msgInServiceFg", "msgInServiceFgSelected", "msgOutServiceFg", "msgOutServiceFgSelected",
    "msgInDateFg", "msgInDateFgSelected", "msgOutDateFg", "msgOutDateFgSelected",
    "msgServiceFg", "historyFileInRadialFg", "historyFileOutRadialFg",
    "historyFileThumbRadialFg", "mediaPlayerInactiveFg", "mediaPlayerDisabledFg",
    "mediaviewFileSizeFg", "callStatusFg", "callCancelFg", "notificationSampleCloseFg",
    "emojiIconFg", "sideBarTextFg", "sideBarIconFg", "overviewCheckBorder",
}

USERPIC = [ACCENT, ACCENT_GREEN, ACCENT_LIME, ACCENT_BRIGHT,
           "#0b6530", "#2bbf68", TEXT, "#ff6688"]
FALLBACK_KEYS: list[str] = []


def color_for(key: str, original: str) -> str:
    """Return a fully explicit 0xPrivacy color for every official palette key."""
    # Preserve white as the transparent-image backing color; it is not UI chrome.
    if key == "imageBgTransparent":
        return "#ffffff"

    # Semantic warning/error states use rose-red rather than green.
    if any(tag in key for tag in ("Error", "Missed", "RedCorner", "reportSpam")) or key.startswith("attentionButton") or key.startswith("callHangup"):
        if "Bg" in key:
            return BG_RED if "Ripple" not in key else "#ff2e6344"
        return RED_BRIGHT if "Over" in key or "Ripple" in key else RED
    if "YellowCorner" in key:
        return ACCENT_LIME_BRIGHT
    if "GreenCorner" in key:
        return ACCENT
    if "BlueCorner" in key:
        return ACCENT_GREEN

    # Small, intentional exception: call-cancel is a neutral action, not an error.
    if key == "callCancelBg":
        return BG_SURFACE
    if key == "callCancelFg":
        return TEXT
    if key == "callCancelRipple":
        return "#39ff1430"

    if key in DARK_ON_ACCENT_FG:
        return BG_DARK

    if key == "callBarBg":
        return BG_SELECTED
    if key == "callBarBgMuted":
        return BG_SURFACE
    if key == "trayCounterBgMute":
        return ACCENT_DEEP
    if key == "callAnswerBgOuter":
        return "#39ff1438"
    if key in ACCENT_BG_KEYS:
        if "Ripple" in key:
            return "#39ff1430"
        return ACCENT_BRIGHT if "Over" in key else ACCENT

    # Root panels and layered surfaces use green-black instead of upstream teal.
    if key in ROOT_BACKGROUNDS:
        return BG_DARK if key in {"introBg", "mediaviewBg", "mediaviewVideoBg", "imageBg", "sideBarBg"} else BG
    if key in DARK_BACKGROUNDS:
        return BG_DARK
    if key in SURFACE_BACKGROUNDS:
        return BG_SURFACE
    if key in {"boxTextFgError", "introErrorFg"}:
        return RED

    # Selected chats and message bubbles; incoming stays neutral-green, outgoing
    # uses the desktop's dark selection green, with bright selected-state contrast.
    if key == "dialogsBgActive":
        return BG_SELECTED
    if key.startswith("dialogsUnreadBgMuted"):
        return ACCENT_DEEP
    if key.startswith("dialogsUnreadBg"):
        return ACCENT
    if key.startswith("dialogsVerifiedIconBg"):
        return ACCENT
    if key.startswith("dialogsBg"):
        return BG_HOVER if "Over" in key else BG
    if key.startswith("historyPeer") and "UserpicBg" in key:
        match = re.search(r"historyPeer(\d+)", key)
        return USERPIC[(int(match.group(1)) - 1) % len(USERPIC)] if match else ACCENT_DEEP
    if key.startswith("msgIn") and "Bg" in key:
        return BG_SELECTED_HI if "Selected" in key else BG_SURFACE
    if key.startswith("msgOut") and "Bg" in key:
        return BG_SELECTED_HI if "Selected" in key else BG_SELECTED
    if key.startswith("msgService") and "Bg" in key:
        return BG_SELECTED
    if key.startswith("msgFile") and "Bg" in key:
        return BG_SELECTED_HI if "Selected" in key else BG_SURFACE

    # Transparent interaction states use the theme accent rather than upstream teal.
    if "Ripple" in key:
        return "#39ff1430"
    if key in {"shadowFg", "windowShadowFg", "windowShadowFgFallback", "slideFadeOutShadowFg", "titleShadow", "historyToDownShadow", "msgInShadow", "msgInShadowSelected", "msgOutShadow", "msgOutShadowSelected"}:
        return "#00000055"
    if key in {"slideFadeOutBg", "photoCropFadeBg", "mediaviewTransparentBg", "notificationsBoxScreenBg"}:
        return "#010402aa"
    if key == "shadowFg":
        return "#00000024"

    # Scrollbars and darkened borders.
    if key.startswith("scrollBar"):
        return "#39ff1466" if "Over" in key else "#39ff1444"
    if key.startswith("scrollBg"):
        return "#09180e88" if "Over" in key else "#09180e55"
    if key in {"inputBorderFg", "filterInputBorderFg", "menuSeparatorFg", "historyUnreadBarBorder"}:
        return ACCENT_DEEP

    # Bright controls and status indicators.
    if key in {"activeLineFg", "outlineButtonOutlineFg", "lightButtonFg", "lightButtonFgOver", "radialFg", "placeholderFgActive", "sliderBgActive", "dialogsOnlineBadgeFg", "profileStatusFgOver", "historyUnreadBarBorder", "historyLinkInFg", "historyLinkInFgSelected", "historyLinkOutFg", "historyLinkOutFgSelected", "msgFileThumbLinkInFg", "msgFileThumbLinkInFgSelected", "msgFileThumbLinkOutFg", "msgFileThumbLinkOutFgSelected", "historyComposeIconFg", "historyReplyIconFg", "historyReplyCancelFgOver", "historyCallArrowInFg", "historyCallArrowOutFg", "historyFileInIconFg", "historyFileInIconFgSelected", "historyFileOutIconFg", "historyFileOutIconFgSelected", "historyFileThumbIconFg", "historyFileThumbIconFgSelected", "msgBotKbIconFg", "historySendIconFgOver", "emojiIconFgActive", "sideBarTextFgActive", "sideBarIconFgActive", "sideBarBadgeBg", "importantTooltipFgLink", "activeButtonSecondaryFg", "activeButtonSecondaryFgOver", "boxTextFgGood", "introCoverIconsFg", "profileAdminStartFg", "callArrowFg", "mediaPlayerActiveFg"}:
        return ACCENT_BRIGHT if "Over" in key or "Selected" in key else ACCENT

    if key in MUTED_FG_EXACT or any(tag in key for tag in ("SubText", "Additional", "Disabled", "Placeholder", "DateFg", "StatusFg", "DraftFg", "ServiceFg", "SeparatorFg", "AboutLimit", "FileSize", "CloseIcon", "MutedFg", "InactiveFg")):
        return TEXT_DISABLED if "Disabled" in key or "Separator" in key else TEXT_MUTED

    if key in {"dialogsTextFgActive", "dialogsNameFgActive", "dialogsDraftFgActive", "dialogsTextFgOver", "dialogsNameFgOver"}:
        return TEXT if key == "dialogsTextFgActive" else ACCENT_BRIGHT
    if key.startswith("historyPeer") and "NameFg" in key:
        if "Selected" in key:
            return TEXT
        match = re.search(r"historyPeer(\d+)", key)
        return USERPIC[(int(match.group(1)) - 1) % len(USERPIC)] if match else ACCENT

    # Apply green phosphor to active labels, links, icons, and selections.
    if "Link" in key or "Online" in key or "Verified" in key or key.endswith("FgActive") or key.endswith("FgOver"):
        return ACCENT_BRIGHT if "Over" in key or "Selected" in key else ACCENT

    # Non-foreground accents, overlays, illustrations, and waveforms.
    other = {
        "titleShadow": "#00000055",
        "introCoverPlaneTrace": "#39ff1470",
        "introCoverPlaneInner": ACCENT_DEEP,
        "introCoverPlaneOuter": ACCENT,
        "introCoverPlaneTop": ACCENT_BRIGHT,
        "emojiPanCategories": TEXT_MUTED,
        "historyUnreadBarBorder": ACCENT,
        "msgSelectOverlay": "#39ff1438",
        "msgStickerOverlay": "#020304aa",
        "msgInReplyBarColor": ACCENT,
        "msgInReplyBarSelColor": ACCENT_BRIGHT,
        "msgOutReplyBarColor": ACCENT,
        "msgOutReplyBarSelColor": ACCENT_BRIGHT,
        "msgImgReplyBarColor": ACCENT,
        "msgWaveformInActive": ACCENT,
        "msgWaveformInActiveSelected": ACCENT_BRIGHT,
        "msgWaveformInInactive": TEXT_MUTED,
        "msgWaveformInInactiveSelected": ACCENT_DEEP,
        "msgWaveformOutActive": ACCENT,
        "msgWaveformOutActiveSelected": ACCENT_BRIGHT,
        "msgWaveformOutInactive": TEXT_MUTED,
        "msgWaveformOutInactiveSelected": ACCENT_DEEP,
        "historyToDownShadow": "#00000055",
        "overviewPhotoSelectOverlay": "#39ff1438",
        "changePhoneSimcardFrom": ACCENT_GREEN,
        "changePhoneSimcardTo": ACCENT,
        "mediaviewPlaybackActive": ACCENT,
        "mediaviewPlaybackInactive": TEXT_MUTED,
        "mediaviewPlaybackActiveOver": ACCENT_BRIGHT,
        "mediaviewPlaybackInactiveOver": ACCENT,
        "callAnswerRipple": ACCENT_BRIGHT,
        "callAnswerBgOuter": "#39ff1438",
        "callMuteRipple": "#39ff1430",
        "callBarMuteRipple": "#39ff1430",
        "callBarUnmuteRipple": "#39ff1430",
        "statisticsChartInactive": "#15512c88",
        "statisticsChartActive": "#39ff1488",
    }
    if key in other:
        return other[key]

    # General-purpose fallbacks are still in-palette and ensure future upstream
    # additions receive a sensible theme color instead of inheriting teal.
    FALLBACK_KEYS.append(key)
    if "Bg" in key or "Background" in key or "Fill" in key:
        if "Selected" in key or "Active" in key:
            return BG_SELECTED
        if "Over" in key:
            return BG_HOVER
        return BG_SURFACE
    if key.endswith("Fg") or "Icon" in key or "Text" in key:
        return TEXT
    return ACCENT


def make_background() -> bytes:
    width, height = 1600, 900
    image = Image.new("RGB", (width, height), BG_DARK)
    # A very restrained phosphor haze behind the faint terminal grid.
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse((width * 0.24, height * 0.14, width * 0.76, height * 0.88), fill=(0, 45, 12, 38))
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, width, 80):
        gd.line((x, 0, x, height), fill=(10, 30, 12, 32), width=1)
    for y in range(0, height, 80):
        gd.line((0, y, width, y), fill=(10, 30, 12, 30), width=1)
    for x in range(0, width, 160):
        for y in range(0, height, 160):
            gd.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(40, 90, 35, 48))
    image = Image.alpha_composite(image.convert("RGBA"), grid).convert("RGB")
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def main() -> None:
    request = urllib.request.Request(UPSTREAM_URL, headers={"User-Agent": "0xPrivacy-theme-builder/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        reference = response.read()
    with zipfile.ZipFile(io.BytesIO(reference)) as upstream:
        if "colors.tdesktop-theme" not in upstream.namelist():
            raise RuntimeError("Telegram's official reference archive has no colors.tdesktop-theme")
        base = upstream.read("colors.tdesktop-theme").decode("utf-8")

    output_lines = [
        "// 0xPrivacy Phosphor · complete Telegram Desktop palette.",
        f"// Based on Telegram Desktop's official night-green palette at {UPSTREAM_COMMIT}.",
    ]
    keys = []
    FALLBACK_KEYS.clear()
    for line in base.splitlines():
        match = LINE_RE.match(line)
        if not match:
            output_lines.append(line)
            continue
        indent, key, original, suffix = match.groups()
        keys.append(key)
        value = color_for(key, original.strip())
        output_lines.append(f"{indent}{key}: {value};{suffix.rstrip()}")
    fallbacks = sorted(set(FALLBACK_KEYS))

    if len(keys) < 400 or len(set(keys)) != len(keys):
        raise RuntimeError(f"Unexpected upstream palette: {len(keys)} keys, {len(set(keys))} unique")
    palette = "\n".join(output_lines) + "\n"
    (OUT / "colors.tdesktop-theme").write_text(palette, encoding="utf-8")
    wallpaper = make_background()
    (OUT / "background.png").write_bytes(wallpaper)

    expanded_bundle = OUT / "0xPrivacy-Phosphor"
    expanded_bundle.mkdir(parents=True, exist_ok=True)
    (expanded_bundle / "colors.tdesktop-theme").write_text(palette, encoding="utf-8")
    (expanded_bundle / "background.png").write_bytes(wallpaper)

    archive_path = OUT / "0xPrivacy-Phosphor.tdesktop-theme"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as theme:
        theme.writestr("colors.tdesktop-theme", palette)
        theme.writestr("background.png", wallpaper)

    with zipfile.ZipFile(archive_path) as check:
        bad = check.testzip()
        if bad:
            raise RuntimeError(f"Theme archive verification failed at {bad}")
        entries = check.namelist()
    print(f"Theme: {archive_path}")
    print(f"Palette: {len(keys)} complete color entries ({len(set(keys))} unique keys)")
    print(f"Archive contents: {', '.join(entries)}")
    print(f"Palette entries using fallback rules: {len(fallbacks)}")
    if fallbacks:
        print("Fallback keys:", ", ".join(fallbacks))
    print(f"Wallpaper: {OUT / 'background.png'} ({len(wallpaper)} bytes)")


if __name__ == "__main__":
    main()
