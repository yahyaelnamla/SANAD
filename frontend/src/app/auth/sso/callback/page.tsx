"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { PageLoader } from "@/components/PageLoader";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";

function SsoCallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { completeSso } = useAuth();
  const { t } = useTranslations();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const provider = searchParams.get("provider") as "google" | "microsoft" | null;
    const code = searchParams.get("code");
    if (!provider || !code) {
      setError(t("auth.ssoFailed"));
      return;
    }
    void completeSso({ provider, code })
      .then((needsOnboarding) => {
        router.replace(needsOnboarding ? "/onboarding" : "/chat");
      })
      .catch(() => setError(t("auth.ssoFailed")));
  }, [searchParams, completeSso, router, t]);

  if (error) {
    return <p className="mx-auto max-w-md text-center text-sm text-destructive">{error}</p>;
  }

  return <PageLoader />;
}

export default function SsoCallbackPage() {
  return (
    <Suspense fallback={<PageLoader />}>
      <SsoCallbackContent />
    </Suspense>
  );
}
