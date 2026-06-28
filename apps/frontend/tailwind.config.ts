import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        carbon: {
          ink: "#17211b",
          panel: "#f7faf8",
          line: "#d9e2dc",
          green: "#1f8a5b",
          amber: "#b7791f",
          blue: "#2563eb"
        }
      }
    }
  },
  plugins: []
} satisfies Config;
