# 0xPrivacy Dark-Web Phosphor Screensaver

The screensaver is the 0xHermes wallpaper animated: rose scan, phosphor shear, and margin rain. One 6-second loop at 12 FPS, not a reel of other pictures.

## Install into Omarchy

After installing this theme, run:

```bash
bash ~/.config/omarchy/themes/0xprivacy/screensaver/install.sh
```

The installer copies the profile to `~/.config/omarchy/branding/screensavers/saved-0xprivacy`. It does **not** change which profile is selected. To activate it explicitly:

```bash
omarchy-screensaver-profile set saved-0xprivacy
```

Use `omarchy-screensaver-profile demo` to preview the selected profile, or wait for the normal idle trigger. Profile selection is separate from the theme's wallpaper picker.

## Runtime

- Python 3 and a true-color terminal are required; there are no third-party Python modules.
- The runner finds `privacy.py` relative to itself.
- Default animation rate is 12 FPS; do not raise it on this thermally constrained laptop.
- The runner uses low CPU/IO priority and restores cursor visibility when it exits.
- `OMARCHY_SAVER_FPS` can override the rate if needed.
