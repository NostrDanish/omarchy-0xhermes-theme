-- Quit the 0xHermes screensaver on any ordinary key or click.
local function quit()
  mp.command("quit 0")
end

local keys = {
  "ESC", "ENTER", "SPACE", "BS", "TAB", "DEL",
  "UP", "DOWN", "LEFT", "RIGHT",
  "MBTN_LEFT", "MBTN_RIGHT", "MBTN_MID",
}
local alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
for i = 1, #alphabet do
  keys[#keys + 1] = alphabet:sub(i, i)
  keys[#keys + 1] = alphabet:sub(i, i):upper()
end
for _, key in ipairs(keys) do
  mp.add_forced_key_binding(key, "exit-" .. key, quit)
end
