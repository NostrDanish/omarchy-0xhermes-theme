-- 0xHermes v2: crisp phosphor borders, restrained gaps, and light transitions.
-- Blur stays off to keep the desktop fast and predictable.

local active_border = { colors = { "rgba(39ff14ee)", "rgba(ff2e63ee)" }, angle = 45 }
local inactive_border = "rgba(20492eaa)"

hl.config({
  general = {
    gaps_in = 6,
    gaps_out = 12,
    border_size = 1,
    col = {
      active_border = active_border,
      inactive_border = inactive_border,
    },
  },
  decoration = {
    rounding = 8,
    shadow = {
      enabled = true,
      range = 10,
      render_power = 2,
      color = "rgba(00000035)",
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
