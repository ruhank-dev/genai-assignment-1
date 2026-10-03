/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: { ink: { 950: "#0b1020", 900: "#111830", 800: "#1a2342", 700: "#26325c" } },
      boxShadow: { glow: "0 0 0 2px rgba(56,189,248,.8), 0 0 24px rgba(56,189,248,.35)" },
    },
  },
  plugins: [],
};
