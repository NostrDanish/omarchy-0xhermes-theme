-- Prefer ~/.local/bin over /usr/share/omarchy/bin so theme overrides like
-- omarchy-screensaver (0xHermes) win when idle launches the saver.
local home = os.getenv("HOME") or ""
local local_bin = home .. "/.local/bin"
local kept = {}

for entry in (os.getenv("PATH") or ""):gmatch("[^:]+") do
  if entry ~= local_bin then
    table.insert(kept, entry)
  end
end

table.insert(kept, 1, local_bin)
hl.env("PATH", table.concat(kept, ":"))
