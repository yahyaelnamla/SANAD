import type { UserRole } from "@/types/auth";

export function isAdminRole(role: UserRole | undefined): boolean {
  return role === "admin" || role === "reviewer";
}
