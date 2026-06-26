import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        nexus: {
          cyan: "hsl(var(--nexus-cyan))",
          navy: "hsl(var(--nexus-navy))",
        },
        brand: {
          accent: "hsl(var(--brand-accent))",
          "accent-muted": "hsl(var(--brand-accent-muted))",
          "accent-subtle": "hsl(var(--brand-accent-subtle))",
        },
        hero: {
          bg: "hsl(var(--hero-bg))",
        },
        link: "hsl(var(--link))",
        fanar: {
          navy: "#08111F",
          white: "#FFFFFF",
          charcoal: "#17191C",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        arabic: ["var(--font-tajawal)", "var(--font-noto-arabic)", "system-ui", "sans-serif"],
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 8px hsl(var(--brand-accent) / 0.25)" },
          "50%": { boxShadow: "0 0 24px hsl(var(--brand-accent) / 0.45)" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(16px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        floatMotif: {
          "0%, 100%": { transform: "translate(0, 0) rotate(0deg)" },
          "33%": { transform: "translate(12px, -18px) rotate(4deg)" },
          "66%": { transform: "translate(-8px, 10px) rotate(-3deg)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.4s ease-out forwards",
        shimmer: "shimmer 1.5s infinite",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "slide-up": "slideUp 0.5s ease-out forwards",
        "float-motif": "floatMotif 24s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
