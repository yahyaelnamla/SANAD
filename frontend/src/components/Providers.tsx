"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { GlobalBackgroundMount } from "@/components/GlobalBackground";
import { PwaInstallPrompt } from "@/components/PwaInstallPrompt";
import { PwaRegister } from "@/components/PwaRegister";
import { SplashScreen } from "@/components/SplashScreen";
import { ThemeClassSync } from "@/components/ThemeClassSync";
import { ThemeProvider } from "@/components/ThemeProvider";
import { isRtl } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/store/settingsStore";

export function Providers({ children }: { children: React.ReactNode }) {
  const locale = useSettingsStore((state) => state.locale);
  const pathname = usePathname();
  const isChatRoute = pathname === "/chat" || pathname.startsWith("/chat");

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = isRtl(locale) ? "rtl" : "ltr";
  }, [locale]);

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="night-blue"
      themes={["light", "night-blue", "dark-gray", "system"]}
      enableSystem={false}
      storageKey="sanad-theme"
    >
      <ThemeClassSync />
      <GlobalBackgroundMount />
      <div
        className={cn(
          "relative flex flex-col",
          isChatRoute ? "h-dvh max-h-dvh overflow-hidden" : "min-h-screen",
        )}
      >
        <SplashScreen />
        <PwaRegister />
        <AppShell>{children}</AppShell>
        <PwaInstallPrompt />
      </div>
    </ThemeProvider>
  );
}
