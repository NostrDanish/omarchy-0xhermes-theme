return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg = "#020804",
        dark_bg = "#010402",
        darker_bg = "#000201",
        lighter_bg = "#09180e",

        fg = "#c7f5ce",
        dark_fg = "#426b4b",
        light_fg = "#dcffe2",
        bright_fg = "#f2fff4",
        muted = "#63856b",

        red = "#ff2e63",
        yellow = "#a8ff45",
        orange = "#ff6688",
        green = "#39ff14",
        cyan = "#2bbf68",
        blue = "#197d43",
        magenta = "#ff6688",
        brown = "#254a31",

        bright_red = "#ff7390",
        bright_yellow = "#c1ff6b",
        bright_green = "#83ff60",
        bright_cyan = "#67ea90",
        bright_blue = "#45cf75",
        bright_magenta = "#ff90a6",

        accent = "#39ff14",
        cursor = "#39ff14",
        foreground = "#c7f5ce",
        background = "#020804",
        selection = "#10311b",
        selection_foreground = "#000201",
        selection_background = "#39ff14",
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
