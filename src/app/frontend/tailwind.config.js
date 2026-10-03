/** @type {import('tailwindcss').Config} */
// Design tokens copied 1:1 from the Google Stitch export ("Luminous Studio Glass", report/stitch/DESIGN.md).
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "secondary-fixed-dim": "#b9c3ff", "primary-fixed": "#ffddb8", "surface-container-highest": "#d9e3f1",
        "secondary-container": "#4868f1", "inverse-on-surface": "#e8f2ff", "tertiary-fixed-dim": "#4edea3",
        "surface-container": "#e4effd", error: "#ba1a1a", "on-error": "#ffffff", "inverse-primary": "#ffb95f",
        outline: "#867461", "on-primary-container": "#613b00", "secondary-fixed": "#dde1ff", "error-container": "#ffdad6",
        surface: "#f7f9ff", "outline-variant": "#d8c3ad", "inverse-surface": "#27313c", "on-primary-fixed": "#2a1700",
        "on-surface-variant": "#534434", "on-tertiary-fixed": "#002113", "on-tertiary": "#ffffff", "surface-variant": "#d9e3f1",
        "surface-bright": "#f7f9ff", "primary-container": "#f59e0b", "surface-container-low": "#edf4ff", "surface-dim": "#d1dbe8",
        primary: "#855300", "surface-container-lowest": "#ffffff", "on-secondary": "#ffffff", "surface-tint": "#855300",
        "on-secondary-container": "#fffbff", "on-primary": "#ffffff", "on-surface": "#121d26",
        "on-tertiary-fixed-variant": "#005236", "on-secondary-fixed-variant": "#0034c0", tertiary: "#006c49",
        "on-error-container": "#93000a", "surface-container-high": "#dfe9f7", secondary: "#2a4dd7",
        "on-tertiary-container": "#004e34", "primary-fixed-dim": "#ffb95f", background: "#f7f9ff",
        "on-primary-fixed-variant": "#653e00", "tertiary-fixed": "#6ffbbe", "tertiary-container": "#30c88f",
        "on-secondary-fixed": "#001257", "on-background": "#121d26",
      },
      borderRadius: { DEFAULT: "1rem", lg: "2rem", xl: "3rem", full: "9999px" },
      spacing: {
        margin: "1.5rem", "space-md": "1rem", "space-xl": "2rem", gutter: "1.25rem", "space-sm": "0.75rem",
        "space-xs": "0.375rem", "space-lg": "1.5rem",
      },
      fontFamily: {
        "body-sm": ["Inter"], "headline-lg": ["Plus Jakarta Sans"], "headline-md": ["Plus Jakarta Sans"],
        "data-tabular": ["Inter"], "label-prominent": ["Inter"], "body-lg": ["Inter"], "title-card": ["Plus Jakarta Sans"],
        "data-metric": ["Inter"], "body-md": ["Inter"], "label-caption": ["Inter"], "headline-sm": ["Plus Jakarta Sans"],
        "display-hero": ["Plus Jakarta Sans"],
      },
      fontSize: {
        "body-sm": ["13px", { lineHeight: "18px", fontWeight: "400" }],
        "headline-lg": ["28px", { lineHeight: "36px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-md": ["22px", { lineHeight: "28px", letterSpacing: "-0.015em", fontWeight: "600" }],
        "data-tabular": ["12px", { lineHeight: "16px", fontWeight: "600" }],
        "label-prominent": ["13px", { lineHeight: "16px", letterSpacing: "0.01em", fontWeight: "600" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "title-card": ["15px", { lineHeight: "20px", letterSpacing: "-0.005em", fontWeight: "600" }],
        "data-metric": ["24px", { lineHeight: "28px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "label-caption": ["11px", { lineHeight: "14px", letterSpacing: "0.02em", fontWeight: "500" }],
        "headline-sm": ["18px", { lineHeight: "24px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "display-hero": ["36px", { lineHeight: "44px", letterSpacing: "-0.025em", fontWeight: "700" }],
      },
    },
  },
  plugins: [],
};
