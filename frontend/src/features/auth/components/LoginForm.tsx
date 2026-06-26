"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { SsoButtons } from "@/features/auth/components/SsoButtons";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { getAuthErrorMessage } from "@/lib/authErrors";

export function LoginForm() {
  const { t } = useTranslations();
  const { login, isLoading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await login({ email, password });
      router.push("/chat");
    } catch (err) {
      setError(getAuthErrorMessage(err, t("auth.invalidCredentials"), t("auth.networkError")));
    }
  };

  const handleSsoSuccess = (needsOnboarding: boolean) => {
    router.push(needsOnboarding ? "/onboarding" : "/chat");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto w-full max-w-md"
    >
      <Card className="glass-card border-border/50 shadow-lg">
        <CardHeader>
          <CardTitle>{t("auth.loginTitle")}</CardTitle>
          <p className="text-sm text-muted-foreground">{t("auth.loginSubtitle")}</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t("auth.email")}
              required
              autoComplete="email"
            />
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t("auth.password")}
              required
              minLength={8}
              autoComplete="current-password"
            />
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="fanar-btn-primary w-full" disabled={isLoading}>
              {t("auth.loginButton")}
            </Button>
          </form>
          <SsoButtons onSuccess={handleSsoSuccess} />
          <p className="mt-4 text-center text-sm text-muted-foreground">
            {t("auth.noAccount")}{" "}
            <Link href="/register" className="text-primary underline">
              {t("auth.registerLink")}
            </Link>
          </p>
          <p className="mt-2 text-center text-xs text-muted-foreground">
            <Link href="/welcome" className="text-link underline-offset-2 hover:underline">
              {t("landing.viewProduct")}
            </Link>
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
}
