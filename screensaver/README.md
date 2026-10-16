# 0xHermes screensaver

One 12 FPS loop of the with-logo wallpaper: rose scan, phosphor shear, margin rain. Not a slideshow.

## Install

```bash
bash ~/.config/omarchy/themes/0xhermes/screensaver/install.sh
```

That installs `~/.local/bin/omarchy-screensaver`, which idle launches before the stock ttfx saver. It also copies a profile under `~/.config/omarchy/branding/screensavers/saved-0xhermes`.

Preview: `omarchy-launch-screensaver force`  
Stock: `/usr/share/omarchy/bin/omarchy-screensaver`

Do not pass `--fps` to mpv. The video file is already 12 FPS. Any ordinary key quits.
