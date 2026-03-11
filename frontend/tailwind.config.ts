import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff", 100: "#dbeafe", 200: "#bfdbfe", 300: "#93c5fd",
          400: "#60a5fa", 500: "#3b82f6", 600: "#2563eb", 700: "#1d4ed8",
          800: "#1e40af", 900: "#1e3a8a", 950: "#172554",
        },
        secondary: {
          50: "#f0fdfa", 100: "#ccfbf1", 200: "#99f6e4", 300: "#5eead4",
          400: "#2dd4bf", 500: "#14b8a6", 600: "#0d9488", 700: "#0f766e",
          800: "#115e59", 900: "#134e4a",
        },
        success: { 50: "#f0fdf4", 100: "#dcfce7", 500: "#22c55e", 600: "#16a34a", 700: "#15803d" },
        warning: { 50: "#fffbeb", 100: "#fef3c7", 500: "#f59e0b", 600: "#d97706", 700: "#b45309" },
        danger: { 50: "#fef2f2", 100: "#fee2e2", 500: "#ef4444", 600: "#dc2626", 700: "#b91c1c" },
        sidebar: {
          bg: "#0f172a", hover: "#1e293b", active: "#334155",
          text: "#94a3b8", "text-active": "#f8fafc", border: "#1e293b",
        },
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
        "fade-in-scale": "fadeInScale 0.3s ease-out",
        "slide-down": "slideDown 0.2s ease-out",
        "shimmer": "shimmer 1.5s infinite",
        "float": "float 3s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2s ease-out infinite",
      },
      boxShadow: {
        "card": "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)",
        "card-hover": "0 10px 25px -5px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04)",
        "sidebar": "4px 0 15px rgba(0,0,0,0.1)",
        "header": "0 1px 3px rgba(0,0,0,0.05)",
        "modal": "0 25px 50px -12px rgba(0,0,0,0.25)",
        "toast": "0 10px 25px -5px rgba(0,0,0,0.15)",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
export default config;
