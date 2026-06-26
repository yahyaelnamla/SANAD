"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { PageLoader } from "@/components/PageLoader";
import { useAuth } from "@/hooks/useAuth";
import { useStoreHydration } from "@/hooks/useStoreHydration";

const PUBLIC_ROUTES = new Set([
  "/login",
  "/register",
  "/welcome",
  "/auth/sso/callback",
  "/onboarding",
]);

export function OnboardingRedirect() {
  const { isAuthenticated, user, hydrateProfile } = useAuth();
  const router = useRouter();
  const hydrated = useStoreHydration();

  useEffect(() => {
    if (hydrated && isAuthenticated && !user) {
      void hydrateProfile();
    }
  }, [hydrated, isAuthenticated, user, hydrateProfile]);

  useEffect(() => {
    if (!hydrated || !isAuthenticated || !user) return;
    const path = window.location.pathname;
    if (PUBLIC_ROUTES.has(path)) return;
    if (!user.onboarding_completed) {
      router.replace("/onboarding");
    }
  }, [hydrated, isAuthenticated, user, router]);

  return null;
}

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, hydrateProfile } = useAuth();
  const router = useRouter();
  const hydrated = useStoreHydration();

  useEffect(() => {
    if (!hydrated) return;
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (!user) {
      void hydrateProfile();
      return;
    }
    if (user.onboarding_completed) {
      router.replace("/chat");
    }
  }, [hydrated, isAuthenticated, user, hydrateProfile, router]);

  if (!hydrated || !isAuthenticated || !user || user.onboarding_completed) {
    return <PageLoader />;
  }

  return <>{children}</>;
}
