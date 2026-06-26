"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { PageLoader } from "@/components/PageLoader";
import { useAuth } from "@/hooks/useAuth";
import { useStoreHydration } from "@/hooks/useStoreHydration";

interface RedirectIfAuthenticatedProps {
  children: React.ReactNode;
  redirectTo?: string;
}

/** Send logged-in users away from public marketing/auth pages. */
export function RedirectIfAuthenticated({
  children,
  redirectTo = "/chat",
}: RedirectIfAuthenticatedProps) {
  const router = useRouter();
  const hydrated = useStoreHydration();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (hydrated && isAuthenticated) {
      router.replace(redirectTo);
    }
  }, [hydrated, isAuthenticated, redirectTo, router]);

  if (!hydrated || isAuthenticated) {
    return <PageLoader />;
  }

  return <>{children}</>;
}
