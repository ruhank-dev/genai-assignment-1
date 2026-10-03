/** @type {import('tailwindcss').Config} */
// Palette follows the Google Stitch "Luminous Studio Glass" design (see report/stitch/DESIGN.md):
// peach -> butter -> periwinkle gradient, frosted-glass cards, amber/yellow primary, indigo secondary.
// `ink-*` are kept as semantic names for glass layers / dark text so existing components keep working.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Plus Jakarta Sans"', "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      colors: {
        ink: {
          950: "#121d26", // dark text / on-primary
          900: "rgba(255,255,255,0.42)", // glass card
          800: "rgba(255,255,255,0.62)", // inner glass / tracks
          700: "rgba(255,255,255,0.85)", // glass borders
        },
        accent: { DEFAULT: "#f59e0b", soft: "#facc15", indigo: "#2a4dd7", mint: "#30c88f" },
      },
      boxShadow: {
        glow: "0 0 0 2px rgba(245,158,11,.85), 0 8px 28px rgba(245,158,11,.30)",
        glass: "0 10px 30px -12px rgba(80,90,140,.25), inset 0 1px 0 rgba(255,255,255,.7)",
      },
      borderRadius: { glass: "1.75rem" },
    },
  },
  plugins: [],
};
