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
import { useSettingsStore } from "@/store/settingsStore";

export function RegisterForm() {
  const { t, locale } = useTranslations();
  const { register, isLoading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await register({ email, password, locale: useSettingsStore.getState().locale });
      router.push("/onboarding");
    } catch (err) {
      setError(getAuthErrorMessage(err, t("auth.registerFailed"), t("auth.networkError")));
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
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle>{t("auth.registerTitle")}</CardTitle>
          <p className="text-sm text-muted-foreground">{t("auth.registerSubtitle")}</p>
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
              autoComplete="new-password"
            />
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {t("auth.registerButton")}
            </Button>
          </form>
          <SsoButtons onSuccess={handleSsoSuccess} />
          <p className="mt-4 text-center text-sm text-muted-foreground">
            {t("auth.hasAccount")}{" "}
            <Link href="/login" className="text-primary underline">
              {t("auth.loginLink")}
            </Link>
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
}
