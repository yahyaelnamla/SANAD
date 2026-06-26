/** Fanar-aligned theme identifiers used by next-themes (html class). */
export const APP_THEMES = ["light", "night-blue", "dark-gray", "system"] as const;

export type AppTheme = (typeof APP_THEMES)[number];

export type ResolvedTheme = "light" | "night-blue" | "dark-gray";

export const DEFAULT_THEME: ResolvedTheme = "night-blue";

export const RESOLVED_THEMES: ResolvedTheme[] = ["light", "night-blue", "dark-gray"];

export const THEME_SWATCHES: Record<ResolvedTheme, string> = {
  light: "#FFFFFF",
  "night-blue": "#08111F",
  "dark-gray": "#17191C",
};

/** Migrate legacy next-themes value. */
export function normalizeTheme(theme: string | undefined): AppTheme {
  if (!theme) return DEFAULT_THEME;
  if (theme === "dark") return "night-blue";
  if (APP_THEMES.includes(theme as AppTheme)) return theme as AppTheme;
  return DEFAULT_THEME;
}

export function isDarkTheme(theme: string | undefined): boolean {
  if (!theme) return true;
  if (theme === "light") return false;
  if (theme === "system") return false;
  return theme === "night-blue" || theme === "dark-gray" || theme === "dark";
}
