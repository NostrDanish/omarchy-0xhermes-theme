# 0xHermes screensaver

One 12 FPS loop of the with-logo wallpaper: rose scan, phosphor shear, margin rain. Not a slideshow.

## Install

```bash
bash ~/.config/omarchy/themes/0xhermes/screensaver/install.sh
```

That installs `~/.local/bin/omarchy-screensaver` and `~/.config/hypr/prefer-local-bin.lua`. Omarchy prepends `$OMARCHY_PATH/bin` to PATH, so without the Hyprland fix idle still runs the stock ttfx ASCII saver (often still branded 0xPRIVACY).

Preview: `omarchy-launch-screensaver force`  
Stock: `/usr/share/omarchy/bin/omarchy-screensaver`  
If preview still shows ASCII: `hyprctl reload`, then preview again.

Do not pass `--fps` to mpv. The video file is already 12 FPS. Any ordinary key quits.
