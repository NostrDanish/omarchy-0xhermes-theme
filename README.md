# 0xHermes

Omarchy theme for 0xPrivacy: forest-black surfaces, neon green `#39ff14`, rose signal `#ff2e63`, the 0xHermes wallpaper, and a 12 FPS screensaver of that same wallpaper.

## Install

```bash
omarchy theme install https://github.com/NostrDanish/0xHermes
omarchy theme set 0xHermes
```

If this checkout is already on disk, point Omarchy at it with a symlink. A bare git directory is treated as untrusted and Omarchy will drop `hyprland.lua`, `neovim.lua`, and `vscode.json`.

```bash
ln -sfn "$PWD" ~/.config/omarchy/themes/0xHermes
omarchy theme set 0xHermes
omarchy theme bg set ~/.config/omarchy/themes/0xHermes/backgrounds/0xhermes.png
```

## Screensaver

Omarchy does not install a screensaver when it applies a theme. After the theme is in place:

```bash
bash screensaver/install.sh
omarchy-screensaver-profile set saved-0xprivacy
```

The attract is `screensaver/hermes-crazy.mp4`: the 0xHermes wallpaper with a rose scan, phosphor shear, and margin rain. One 6-second loop at 12 FPS. Any ordinary key quits.

## Icons

`icons.theme` names `0xPrivacy-Phosphor`. Regenerate the green/red launcher covers after installing or removing apps:

```bash
/usr/bin/python3 generate-app-icons.py
gsettings set org.gnome.desktop.interface icon-theme '0xPrivacy-Phosphor'
```

Bright ink is neon green. Dark ink is rose.

## Palette

| Role | Hex |
|---|---|
| Background | `#020804` |
| Neon green | `#39ff14` |
| Rose signal | `#ff2e63` |
| Text | `#c7f5ce` |
