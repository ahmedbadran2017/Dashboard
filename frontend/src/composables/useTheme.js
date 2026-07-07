// Light/dark theme, persisted. Sets data-theme on <html> so the CSS variable
// overrides in index.css take effect (300ms bg transition). Defaults to the
// system preference on first load.
import { ref } from "vue";

const STORAGE_KEY = "ops.theme";

function initial() {
  if (typeof localStorage !== "undefined") {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "dark" || saved === "light") return saved;
  }
  if (typeof window !== "undefined" && window.matchMedia) {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return "light";
}

const theme = ref(initial());

export function applyThemeToRoot() {
  document.documentElement.setAttribute("data-theme", theme.value);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", theme.value === "dark" ? "#131417" : "#ffffff");
}

export function useTheme() {
  function toggle() {
    theme.value = theme.value === "dark" ? "light" : "dark";
    if (typeof localStorage !== "undefined") localStorage.setItem(STORAGE_KEY, theme.value);
    applyThemeToRoot();
  }
  return { theme, toggle };
}
