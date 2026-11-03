// Quick Dungeon: theme. Dark is the default; picking light with the header toggle (site.js)
// saves it here. This runs as a blocking script in <head> so a saved light theme is applied
// before the first paint instead of flashing dark.
try {
  if (localStorage.getItem("theme") === "light") document.documentElement.dataset.theme = "light";
} catch {
  // storage blocked (some privacy modes): stay dark
}
