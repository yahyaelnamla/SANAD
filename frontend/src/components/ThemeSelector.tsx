"use client";

import { Check, Monitor, Moon, Palette, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useTranslations } from "@/hooks/useTranslations";
import {
  APP_THEMES,
  normalizeTheme,
  RESOLVED_THEMES,
  THEME_SWATCHES,
  type AppTheme,
  type ResolvedTheme,
} from "@/lib/themes";
import { cn } from "@/lib/utils";

const THEME_ICONS: Record<ResolvedTheme, typeof Sun> = {
  light: Sun,
  "night-blue": Moon,
  "dark-gray": Palette,
};

interface ThemeSelectorProps {
  variant?: "icon" | "segmented";
}

export function ThemeSelector({ variant = "icon" }: ThemeSelectorProps) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const { t } = useTranslations();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!mounted || !theme) return;
    const normalized = normalizeTheme(theme);
    if (normalized !== theme) setTheme(normalized);
  }, [mounted, theme, setTheme]);

  const activeResolved = normalizeTheme(resolvedTheme ?? theme) as ResolvedTheme | "system";
  const displayResolved =
    activeResolved === "system"
      ? (normalizeTheme(resolvedTheme) as ResolvedTheme)
      : (activeResolved as ResolvedTheme);

  const labelFor = (id: AppTheme) => {
    if (id === "system") return t("settings.themeSystem");
    if (id === "light") return t("settings.themeLight");
    if (id === "night-blue") return t("settings.themeNightBlue");
    return t("settings.themeDarkGray");
  };

  if (!mounted) {
    return variant === "segmented" ? (
      <div className="h-10 w-full max-w-sm rounded-xl skeleton-block" aria-hidden />
    ) : (
      <Button
        variant="ghost"
        size="icon"
        className="inline-flex h-9 w-9 items-center justify-center"
        aria-label={t("settings.theme")}
      />
    );
  }

  if (variant === "segmented") {
    return (
      <div
        className="flex flex-wrap gap-2"
        role="radiogroup"
        aria-label={t("settings.theme")}
      >
        {RESOLVED_THEMES.map((id) => {
          const Icon = THEME_ICONS[id];
          const selected = displayResolved === id;
          return (
            <button
              key={id}
              type="button"
              role="radio"
              aria-checked={selected}
              onClick={() => setTheme(id)}
              className={cn(
                "flex min-w-[7.5rem] flex-1 items-center gap-2 rounded-xl border px-3 py-2.5 text-sm transition-all duration-300",
                "hover:border-primary/40 hover:bg-muted/50",
                selected
                  ? "border-primary bg-primary/10 text-foreground shadow-sm ring-1 ring-primary/25"
                  : "border-border/60 bg-card/50 text-muted-foreground",
              )}
            >
              <span
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-border/50"
                style={{ backgroundColor: THEME_SWATCHES[id] }}
              >
                <Icon className="h-3.5 w-3.5 text-foreground/80 mix-blend-difference" />
              </span>
              <span className="font-medium">{labelFor(id)}</span>
              {selected && <Check className="ms-auto h-4 w-4 text-primary" />}
            </button>
          );
        })}
        <button
          type="button"
          role="radio"
          aria-checked={activeResolved === "system"}
          onClick={() => setTheme("system")}
          className={cn(
            "flex min-w-[7.5rem] flex-1 items-center gap-2 rounded-xl border px-3 py-2.5 text-sm transition-all duration-300",
            "hover:border-primary/40 hover:bg-muted/50",
            activeResolved === "system"
              ? "border-primary bg-primary/10 text-foreground shadow-sm ring-1 ring-primary/25"
              : "border-border/60 bg-card/50 text-muted-foreground",
          )}
        >
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-border/50 bg-muted">
            <Monitor className="h-3.5 w-3.5" />
          </span>
          <span className="font-medium">{labelFor("system")}</span>
          {activeResolved === "system" && <Check className="ms-auto h-4 w-4 text-primary" />}
        </button>
      </div>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="inline-flex h-9 w-9 items-center justify-center"
          aria-label={t("settings.theme")}
        >
          {displayResolved === "light" ? (
            <Sun className="h-4 w-4" />
          ) : displayResolved === "dark-gray" ? (
            <Palette className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-[200px]">
        <DropdownMenuLabel>{t("settings.theme")}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {APP_THEMES.map((id) => {
          const selected =
            id === "system" ? activeResolved === "system" : displayResolved === id && activeResolved !== "system";
          const Icon =
            id === "system"
              ? Monitor
              : id === "light"
                ? Sun
                : id === "night-blue"
                  ? Moon
                  : Palette;
          const swatch = id !== "system" ? THEME_SWATCHES[id as ResolvedTheme] : undefined;
          return (
            <DropdownMenuItem
              key={id}
              onClick={() => setTheme(id)}
              className="gap-2"
            >
              {swatch ? (
                <span
                  className="h-4 w-4 shrink-0 rounded-full border border-border/60"
                  style={{ backgroundColor: swatch }}
                />
              ) : (
                <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
              )}
              <span className="flex-1">{labelFor(id)}</span>
              {selected && <Check className="h-4 w-4 text-primary" />}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
