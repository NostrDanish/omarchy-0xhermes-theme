# 0xPrivacy Telegram Desktop theme

**`0xPrivacy-Phosphor.tdesktop-theme`** is the importable Telegram Desktop theme bundle. It contains a complete 467-entry `colors.tdesktop-theme` palette and a custom low-contrast phosphor-grid chat background.

The palette follows the 0xPrivacy dark-web theme: deep green-black `#020804`, forest-green surfaces `#09180e`, neon green `#39ff14`, pale-green text `#c7f5ce`, and rose-red `#ff2e63` signal accents. The color-key schema is based on Telegram Desktop's official `night-green.tdesktop-theme` at commit `1e66d5874c973b9b573492796cbb641152c03f3c`.

## Apply in Telegram Desktop

Open **Settings → Chat Settings → ⋮ → Create New Theme → Import Existing Theme**, then select `0xPrivacy-Phosphor.tdesktop-theme`.

## Regenerate

Run `/usr/bin/python3 ~/.config/omarchy/themes/0xprivacy/generate-telegram-theme.py`. The generator downloads the pinned official reference palette, applies the 0xPrivacy dark-web color roles, and rebuilds the bundle plus its readable palette and wallpaper beside this README.
