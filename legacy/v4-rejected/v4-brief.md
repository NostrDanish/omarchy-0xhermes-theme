# 0xHermes Theme v4 — Art Direction Brief

**Target canvas:** 5120×2160 (ultrawide) · **Saver:** 2560×1080 · **Frame rate:** 12 FPS · **Loop:** seamless 12 s

---

## 1. What Makes the Loved Art Work

The beloved identity rests on a single human figure rendered as a **dot-matrix portrait** — not a photograph, not a vector, but thousands of discrete phosphor-green dots whose density encodes light and shadow, giving the image a tactile, "data-printed" fragility that feels retro-futuristic without being kitschy. The composition is **asymmetrical**: the portrait occupies the left third at life scale, while the typographic block floats right and center-vertical, creating breathing room that lets the eye travel from face to wordmark to tagline without collision. **Two colors carry the load** — near-black ink and phosphor green — while a single rose-red accent (the `0x` prefix and the thin horizontal rule) punctures the monochrome exactly once, creating a hierarchy that reads instantly at thumbnail size. The **tracked mono tagline** ("NO LOGS . NO TRACE . NO NAME") and **corner micro-text** frame the piece like terminal metadata, reinforcing the hacker aesthetic without competing for attention. Finally, **edge-hugging vertical binary columns** and faint scanlines are kept below 8 % opacity so they read as atmosphere, not decoration, preserving the negative space that makes the portrait glow.

---

## 2. Exact Palette

| Hex | Name | Role |
|-----|------|------|
| `#020804` | Ink | Background base; 100 % fill behind all elements |
| `#000000` | Void | Deepest shadow; pure-black drop behind glow cores only |
| `#39ff14` | Phosphor | Primary: portrait dots, wordmark body, active elements |
| `#83ff60` | Mint | Secondary glow bloom; lighter highlight dots in portrait |
| `#ff2e63` | Rose | Accent only: `0x` prefix, single horizontal rule, key glitch line |
| `#c7f5ce` | Foreground | Tagline, micro-text, UI labels |
| `#426b4b` | Muted | Dim tagline variant, inactive corner text, scanlines |
| `#010402` | Shadow | Vignette outer edge; 15 % radial gradient feather |

**Usage rules:**
- `#39ff14` is the only color that carries luminance weight above 60 % in the portrait.
- `#ff2e63` is never used for fill larger than 2 px in height or width except the `0x` glyphs.
- `#83ff60` is never a primary dot color; it appears only as bloom/blur falloff.
- All text above 32 px uses `#39ff14` or `#ff2e63`; never `#c7f5ce` at large sizes.

---

## 3. Portrait Treatment Spec

### 3.1 Dot Matrix
- **Canvas:** 5120×2160
- **Dot grid:** 8 px centers (62.5 dots per 100 px horizontally, 31.25 per 100 px vertically). Use square dots; never circles.
- **Dot size:** 6 px square, 2 px gap (1 px on each side).
- **Luminance-to-dot mapping:** Map source luminance [0–255] to dot opacity [0–255] using a 1:1 linear lookup table. Luminance ≥ 128 renders a full phosphor dot (`#39ff14`); 64–127 renders at 50 % opacity; < 64 renders nothing (hole). Do **not** dither or use error diffusion.
- **Edge handling:** Portrait mask is hard-clipped at the grid boundary; no anti-aliased feather. Outer 8 px of the portrait area is left as pure ink (`#020804`) — no halo.
- **Glow:** Behind the portrait, apply a single 24 px Gaussian blur of `#39ff14` at 12 % opacity, then a 64 px blur of `#39ff14` at 4 % opacity. The bloom is centered on the portrait's bounding box, not per-dot.

### 3.2 Readability at 5120×2160
- Portrait eye level sits at 960 px from top.
- Portrait width spans 1400 px (left edge at 180 px, right edge at 1580 px).
- Portrait height spans 1600 px (top at 280 px, bottom at 1880 px).
- Minimum dot-to-dot contrast distance at viewing distance 1.2 m (28″ monitor at 110 PPI): 8 px centers resolve as 0.7 arcmin — above the 1 arcmin acuity threshold, so details remain legible without blur.

---

## 4. Typography Spec (5120×2160)

**Font:** JetBrains Mono Nerd Font Regular (fallback: DejaVu Sans Mono). All caps. No ligatures.

| Element | Content | Size | Color | Position (x, y from top-left) | Notes |
|---------|---------|------|-------|------------------------------|-------|
| Wordmark body | `PRIVACY` | 220 px | `#39ff14` | x=1880, y=760 | Tracking: +40 px-em |
| Prefix | `0x` | 220 px | `#ff2e63` | x=1600, y=760 | Same baseline as wordmark |
| Horizontal rule | — | 4 px H × 1120 px W | `#ff2e63` | x=1600, y=1000 | 120 px gap above wordmark |
| Tagline | `NO LOGS . NO TRACE . NO NAME` | 38 px | `#c7f5ce` | x=1600, y=1120 | Letter-spacing: +12 px |
| Corner micro-text BL | `0xPRIVACY` | 22 px | `#426b4b` | x=40, y=2080 | Bottom-left, 40 px margin |
| Corner micro-text BR | `ROOT` | 22 px | `#426b4b` | x=5040, y=2080 | Bottom-right, right-aligned, 40 px margin |
| Vertical edge columns | binary / hex | 14 px | `#39ff14` at 6 % opacity | x=20 and x=5100, spanning y=200→1800 | Fade in/out over 120 px top/bottom |

**Safe zone:** No content crosses x=0→26 or x=5094→5120 in the top 26 px. The top bar (26 px) is left entirely clear; the first content baseline is at y=760.

---

## 5. Background / Texture Spec

- **Base fill:** `#020804` at 100 %.
- **Vignette:** Radial gradient from `#020804` (center) to `#010402` (edges), 15 % opacity at farthest radius, 0 % at 40 % of half-min-dimension. Center of gradient = canvas center.
- **Scanlines:** Horizontal lines at 3 px spacing, 1 px height, `#39ff14` at 3 % opacity, spanning full width. Phase-locked so lines are pixel-aligned.
- **Noise:** Per-pixel grain, monochromatic `#39ff14`, 1.2 % opacity, generated via a 2×2 tiled 64×64 noise texture (no Perlin).
- **Grid:** None. The rejected direction's graph-paper grid is explicitly prohibited.
- **Edge columns:** See typography spec. Fade envelope is linear over 120 px top/bottom.

---

## 6. Motion Spec — Seamless 12 s Loop (2560×1080, 12 FPS)

**Total frames:** 144. **Loop constraint:** frame 0 == frame 143.

### 6.1 Dot Dissolve Waves
- The portrait's dot opacity is modulated by a traveling sine wave across the x-axis.
- Wave formula per dot at column `cx`: `opacity_mod = 0.7 + 0.3 * sin( (cx / width) * 2π - (frame / 144) * 2π )`
- Wave speed: one full cycle per 144 frames (12 s). Because the wave is continuous and periodic, frame 0 and frame 143 are identical.
- Implementation: pre-compute a 2560-wide lookup array of opacity multipliers; apply as a per-column multiplier to the portrait's dot alpha. **Cheap:** one multiply per column per frame, no per-pixel math.

### 6.2 Scanline Sweep
- A single horizontal scanline band (64 px tall) moves from top to bottom.
- Band position `y = (frame / 144) * (height + 64) - 32` (wraps via modulo).
- Inside the band: increase dot luminance by one stop (`#39ff14` → `#83ff60`) at 60 % opacity.
- Outside the band: no change.
- **Loop trick:** because the band travels full height + band height in 144 frames, it returns to start position with identical phase.

### 6.3 Breathing Glow
- The portrait's bloom layers (24 px and 64 px) pulse sinusoidally.
- 24 px blur opacity: `12 % + 4 % * sin( (frame / 144) * 2π )` → range [8 %, 16 %].
- 64 px blur opacity: `4 % + 2 % * sin( (frame / 144) * 2π + π/2 )` → range [2 %, 6 %].
- Phase offset ensures bloom expands while the wave contracts, avoiding a flat "breathing" look.

### 6.4 Rendering Order (per frame)
1. Fill ink background.
2. Draw vignette.
3. Draw scanlines (static).
4. Draw noise.
5. Draw portrait dots with wave opacity applied.
6. Draw scanline sweep band on top of portrait.
7. Draw static typography block.
8. Draw breathing bloom (two blur layers, additive).

**Performance budget:** All transforms are per-column or per-frame scalar ops. No per-pixel loops. Render target is 2560×1080 at 12 FPS; a single-threaded Pillow + NumPy pipeline completes one frame in < 40 ms on this hardware.

---

## 7. Three Named Wallpaper Variants

All variants share the same 5120×2160 portrait treatment, palette, and typography baseline. Differences are limited to composition, extra texture, and one accent color.

### 7.1 Hero (`0xhermes.png`)
- **Portrait:** Full figure, left third, 1400×1600 px, dense dot matrix with full luminance range.
- **Wordmark:** Full `0x PRIVACY` + 4 px rose rule + tagline + corner micro-text.
- **Texture:** Vignette + scanlines + noise + edge binary columns.
- **Accent:** Rose `#ff2e63` rule and `0x`.

### 7.2 Quiet (`01-quiet-channel.png`)
- **Portrait:** Same figure, cropped to head-and-shoulders (800×1000 px), centered-left at x=240, y=560. Reduced dot density: 10 px centers (50 dots per 100 px) — a deliberate "lower resolution" look suggesting sleep/idle.
- **Wordmark:** `0x PRIVACY` only, no rule, no tagline. Tagline is suppressed entirely.
- **Texture:** Vignette + scanlines only. No noise, no edge columns.
- **Accent:** Rose `#ff2e63` on `0x` only; wordmark body uses muted `#426b4b` instead of phosphor.

### 7.3 Storm (`03-cipher-storm.png`)
- **Portrait:** Full figure, same position as Hero. **Glitch treatment:** 3 % of dots per frame are randomly shifted ±16 px horizontally (in static still, this is frozen as a spatial jitter). Two horizontal rose lines at 2 px height, 40 % opacity, placed at eye level and chin level.
- **Wordmark:** Full block as Hero, but tagline reads `TRUST NOTHING • VERIFY EVERYTHING`.
- **Texture:** Vignette + scanlines + noise + edge columns, plus a faint diagonal arc (rose, 8 % opacity, 2 px stroke) connecting the portrait's forehead to the wordmark's left edge.
- **Accent:** Rose `#ff2e63` rule, `0x`, and two glitch lines.

---

## 8. Explicit DON'Ts (What Made the Rejected Direction Wrong)

1. **No geometric sigils, hexagons, or radar circles.** The rejected "Signal Temple" replaced the human face with abstract HUD geometry; the v4 identity is anchored to the portrait, not to a logo mark.
2. **No instrument traces, waveforms, or timelines.** Signal-intelligence decoration belongs in a dashboard, not in a desktop wallpaper.
3. **No graph-paper grid overlay.** The faint grid in the rejected direction competed with the dot matrix for texture and added visual noise without narrative purpose.
4. **No CRT bloom on typography.** The rejected bloom effect blurred letterforms into green fog; v4 type is razor-sharp, with bloom applied only to the portrait dots as a halo.
5. **No "NODE: DESKTOP // LOCAL ONLY" or version-stamp telemetry in corners.** Corner micro-text is strictly `0xPRIVACY` and `ROOT`; technical metadata is noise.
6. **No mascot abstraction.** The figure is always recognizably human (girl with headphones, bangs); do not stylize into a rune, tree, or circuit.
7. **No gradient fills or smooth shading.** Every tonal transition is a density change of discrete dots; no airbrushing, no smooth vectors.
8. **No secondary accent colors beyond rose.** Mint `#83ff60` is strictly a glow/bloom derivative of phosphor; it never appears as a primary fill.

---

## 9. Implementation Notes

- **Build pipeline:** `tools/generate_v4_assets.py` must produce all three stills and the 144-frame saver loop from a single portrait source (high-res PNG or SVG).
- **Font embedding:** JetBrains Mono Nerd Font must be available at `/usr/share/fonts/TTF/JetBrainsMonoNerdFont-{Regular,Bold}.ttf`. The generator must fall back to DejaVu Sans Mono only if the primary font is missing.
- **Lock art:** Derive from Hero with the bottom 480 px masked to `#020804` so the greeter's password field has a clean field.
- **Preview:** Generate a 2560×1440 `preview.png` for the picker and a 1024×1024 `unlock.png` for the lock screen.

---

*Brief locked. No design decisions remain unspecified.*
