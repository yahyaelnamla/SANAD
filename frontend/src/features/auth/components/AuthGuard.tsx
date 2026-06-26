"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { ChatPageSkeleton } from "@/components/ChatPageSkeleton";
import { PageLoader } from "@/components/PageLoader";
import { useAuth } from "@/hooks/useAuth";
import { useStoreHydration } from "@/hooks/useStoreHydration";

interface AuthGuardProps {
  children: React.ReactNode;
  variant?: "chat" | "default";
}

export function AuthGuard({ children, variant = "default" }: AuthGuardProps) {
  const { isAuthenticated, hydrateProfile } = useAuth();
  const router = useRouter();
  const hydrated = useStoreHydration();
  const profileRequested = useRef(false);

  useEffect(() => {
    if (!hydrated || !isAuthenticated || profileRequested.current) return;
    profileRequested.current = true;
    void hydrateProfile();
  }, [hydrated, isAuthenticated, hydrateProfile]);

  useEffect(() => {
    if (!hydrated) return;
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [hydrated, isAuthenticated, router]);

  if (!hydrated || !isAuthenticated) {
    if (variant === "chat") {
      return <ChatPageSkeleton />;
    }
    return <PageLoader />;
  }

  return <>{children}</>;
}
