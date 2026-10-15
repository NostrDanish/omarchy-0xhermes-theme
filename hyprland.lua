local active_border_color = { colors = { "rgba(39ff14ee)", "rgba(ff2e63ee)" }, angle = 45 }
local inactive_border_color = "rgba(20492eaa)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },
})
