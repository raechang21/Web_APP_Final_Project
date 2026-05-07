import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "var(--paper)",
        oat: "var(--oat)",
        ink: "var(--ink)",
        mist: "var(--mist)",
        accent: "var(--accent)",
        coral: "var(--coral)",
        sage: "var(--sage)",
        amber: "var(--amber)",
        lavender: "var(--lavender)",
      },
      fontFamily: {
        sans: ["'Noto Sans TC'", "sans-serif"],
        display: ["'Newsreader'", "serif"],
      },
      boxShadow: {
        soft: "0 18px 60px rgba(54, 47, 31, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
