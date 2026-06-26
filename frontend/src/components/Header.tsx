"use client";

import Link from "next/link";
import { Menu, Search } from "lucide-react";
import { useCallback, useState } from "react";

import { GlobalSearchDialog, useGlobalSearchShortcut } from "@/components/GlobalSearchDialog";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UserMenu } from "@/components/UserMenu";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useStoreHydration } from "@/hooks/useStoreHydration";
import { useTranslations } from "@/hooks/useTranslations";
import { useSettingsStore } from "@/store/settingsStore";

export function Header() {
  const { t, locale } = useTranslations();
  const hydrated = useStoreHydration();
  const { isAuthenticated } = useAuth();
  const setMobileSidebarOpen = useSettingsStore((s) => s.setMobileSidebarOpen);
  const [searchOpen, setSearchOpen] = useState(false);
  const openSearch = useCallback(() => setSearchOpen(true), []);
  useGlobalSearchShortcut(openSearch);

  return (
    <header className="theme-zone-dark sticky top-0 z-50 border-b border-border/50 glass-panel">
      <div className="relative flex h-14 items-center px-3 md:px-5">
        {/* Start corner: mobile menu + search */}
        <div className="flex min-w-[88px] items-center gap-1">
          {hydrated && isAuthenticated && (
            <>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-9 w-9 lg:hidden"
                aria-label={t("nav.menu")}
                onClick={() => setMobileSidebarOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={() => setSearchOpen(true)}
                aria-label={t("search.open")}
              >
                <Search className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>

        {/* Center: brand */}
        <Link
          href={hydrated && isAuthenticated ? "/chat" : "/welcome"}
          className="absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 items-center gap-2.5 transition-opacity hover:opacity-90"
        >
          <div className="sanad-brand-icon flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sm font-bold">
            {locale === "ar" ? "س" : "S"}
          </div>
          <span className="sanad-brand-wordmark text-lg tracking-tight">{t("app.name")}</span>
        </Link>

        {/* End corner: utilities */}
        <div className="ms-auto flex items-center gap-1">
          {!hydrated ? (
            <div className="h-9 w-24 rounded-lg skeleton-block" aria-hidden />
          ) : isAuthenticated ? (
            <UserMenu />
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm" className="h-9">
                  {t("auth.loginButton")}
                </Button>
              </Link>
              <Link href="/register" className="hidden sm:block">
                <Button size="sm" className="fanar-btn-primary h-9">
                  {t("auth.registerButton")}
                </Button>
              </Link>
            </>
          )}
          <LanguageSwitcher />
          <ThemeToggle />
        </div>
      </div>
      <GlobalSearchDialog open={searchOpen} onOpenChange={setSearchOpen} />
    </header>
  );
}
