"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { useAuth } from "@/hooks/useAuth";
import { isAdminRole } from "@/lib/roles";

function AdminRoleGate({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user && !isAdminRole(user.role)) {
      router.replace("/chat");
    }
  }, [user, router]);

  if (!user || !isAdminRole(user.role)) {
    return null;
  }

  return <>{children}</>;
}

export function AdminGuard({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <AdminRoleGate>{children}</AdminRoleGate>
    </AuthGuard>
  );
}
