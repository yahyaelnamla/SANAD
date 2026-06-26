"use client";

import { usePathname } from "next/navigation";

import { SkipToContent } from "@/components/SkipToContent";
import { ConnectionStatusBanner } from "@/components/ConnectionStatusBanner";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { OfflineBanner } from "@/components/OfflineBanner";
import { OnboardingRedirect } from "@/features/auth/components/OnboardingGuard";
import { PreferencesBootstrap } from "@/components/PreferencesBootstrap";
import { useOfflineQuerySync } from "@/hooks/useOfflineQuerySync";
import { MobileSidebarDrawer } from "@/components/layout/MobileSidebarDrawer";
import { Sidebar } from "@/components/layout/Sidebar";
import { SidebarSkeleton } from "@/components/layout/SidebarSkeleton";
import { useAuth } from "@/hooks/useAuth";
import { useStoreHydration } from "@/hooks/useStoreHydration";
import { cn } from "@/lib/utils";

const ONBOARDING_EXEMPT_ROUTES = new Set([
  "/login",
  "/register",
  "/welcome",
  "/onboarding",
  "/auth/sso/callback",
]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const hydrated = useStoreHydration();
  const { isAuthenticated } = useAuth();
  const isMarketingRoute = ONBOARDING_EXEMPT_ROUTES.has(pathname);
  const isChatRoute = pathname === "/chat" || pathname.startsWith("/chat");
  const showSidebar = hydrated && isAuthenticated && !isMarketingRoute;
  const showSidebarPlaceholder = !isMarketingRoute && !hydrated;

  useOfflineQuerySync();

  return (
    <div
      className={cn(
        "flex flex-col overflow-x-clip",
        isChatRoute ? "h-dvh max-h-dvh overflow-hidden" : "min-h-screen",
      )}
    >
      <SkipToContent />
      {isAuthenticated && !isMarketingRoute && <OnboardingRedirect />}
      {isAuthenticated && !isMarketingRoute && <PreferencesBootstrap />}
      <Header />
      {!isMarketingRoute && <ConnectionStatusBanner />}
      {!isMarketingRoute && <OfflineBanner />}
      <div
        className={cn(
          "flex min-h-0 flex-1 overflow-hidden",
          !isChatRoute && "min-h-0",
        )}
      >
        {showSidebarPlaceholder && (
          <div className="hidden h-full shrink-0 overflow-hidden lg:block">
            <SidebarSkeleton />
          </div>
        )}
        {showSidebar && (
          <div className="hidden h-full shrink-0 overflow-hidden lg:block">
            <Sidebar />
          </div>
        )}
        {showSidebar && <MobileSidebarDrawer />}
        <main
          id="main-content"
          tabIndex={-1}
          className={cn(
            isChatRoute
              ? "flex min-h-0 flex-1 flex-col overflow-hidden px-2 py-2 md:px-3"
              : "flex-1 px-3 py-6 sm:px-4 sm:py-8",
            isMarketingRoute && !isChatRoute && "auth-page-canvas",
          )}
        >
          {children}
        </main>
      </div>
      {!isChatRoute && <Footer />}
    </div>
  );
}
