/** @type {import('tailwindcss').Config} */
// Tailwind is used for layout utilities only. All colors come from the Justyol
// Design System CSS custom properties (see src/index.css) so light/dark theming
// is a single variable swap on the app root. We map the DS tokens into Tailwind
// so utilities like `text-ink` / `bg-surface` resolve to the live variables.
export default {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--jy-ink)",
        "text-2": "var(--jy-text-2)",
        mute: "var(--jy-mute)",
        "mute-2": "var(--jy-mute-2)",
        line: "var(--jy-line)",
        bg: "var(--jy-bg)",
        "bg-2": "var(--jy-bg-2)",
        surface: "var(--jy-surface)",
        pressed: "var(--jy-pressed)",
        orange: "var(--jy-orange)",
        "orange-soft": "var(--jy-orange-soft)",
        red: "var(--jy-red)",
        "red-tint": "var(--jy-red-tint)",
        green: "var(--jy-green)",
        "green-tint": "var(--jy-green-tint)",
        blue: "var(--jy-blue)",
        "blue-tint": "var(--jy-blue-tint)",
        wa: "var(--jy-wa)",
      },
      fontFamily: {
        sans: ["var(--jy-font)"],
      },
      borderRadius: {
        card: "14px",
        hero: "18px",
        sheet: "18px",
        tile: "12px",
      },
    },
  },
  plugins: [],
};
