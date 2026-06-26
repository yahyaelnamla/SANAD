"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut, Settings, User } from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";

function userInitials(email?: string | null): string {
  if (!email) return "?";
  const local = email.split("@")[0] ?? "";
  return (local.charAt(0) || email.charAt(0)).toUpperCase();
}

export function UserMenu() {
  const router = useRouter();
  const { t } = useTranslations();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push("/welcome");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="h-9 w-9 shrink-0 rounded-full border-border/60 p-0"
          aria-label={t("header.accountMenu")}
        >
          <span className="user-avatar-badge flex h-full w-full items-center justify-center rounded-full text-xs">
            {userInitials(user?.email)}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56 border-border/80 bg-card shadow-xl">
        <DropdownMenuLabel className="flex items-start gap-2 py-2.5">
          <User className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <span className="min-w-0 break-all leading-snug">{user?.email}</span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/settings" className="cursor-pointer">
            <Settings className="h-4 w-4 shrink-0" />
            {t("nav.settings")}
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
          <LogOut className="h-4 w-4 shrink-0" />
          {t("auth.logout")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
