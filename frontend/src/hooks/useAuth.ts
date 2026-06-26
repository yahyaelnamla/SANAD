"use client";

import { useAuthStore } from "@/store/authStore";

export function useAuth() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const user = useAuthStore((s) => s.user);
  const isLoading = useAuthStore((s) => s.isLoading);
  const login = useAuthStore((s) => s.login);
  const register = useAuthStore((s) => s.register);
  const completeSso = useAuthStore((s) => s.completeSso);
  const logout = useAuthStore((s) => s.logout);
  const hydrateProfile = useAuthStore((s) => s.hydrateProfile);

  return {
    accessToken,
    user,
    isLoading,
    isAuthenticated: Boolean(accessToken),
    login,
    register,
    completeSso,
    logout,
    hydrateProfile,
  };
}
