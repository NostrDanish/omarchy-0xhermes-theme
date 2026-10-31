-- 0xHermes v3: phosphor edge on the focused window, rose on its shadow side,
-- and enough gap that the plate reads through. Blur stays off: this desktop is
-- for reading terminals, and translucency only blurs the text behind them.

local active_border = { colors = { "rgba(39ff14dd)", "rgba(ff2e63dd)" }, angle = 45 }
local inactive_border = "rgba(2f7d4faa)"

hl.config({
  general = {
    gaps_in = 6,
    gaps_out = 14,
    border_size = 2,
    resize_on_border = true,
    extend_border_grab_area = 8,
    col = {
      active_border = active_border,
      inactive_border = inactive_border,
    },
  },
  decoration = {
    rounding = 10,
    active_opacity = 1.0,
    inactive_opacity = 0.97,
    dim_inactive = true,
    dim_strength = 0.12,
    shadow = {
      enabled = true,
      range = 18,
      render_power = 3,
      color = "rgba(0000004d)",
    },
    blur = {
      enabled = false,
    },
  },
  group = {
    col = {
      border_active = active_border,
      border_inactive = inactive_border,
    },
  },
})

-- Keep Omarchy's native animation system; only tune window/layer motion.
hl.animation({ leaf = "windows", enabled = true, speed = 4.5, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4, bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 2.5, bezier = "linear", style = "fade" })
