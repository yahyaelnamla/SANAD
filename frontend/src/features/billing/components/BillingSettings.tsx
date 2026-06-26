"use client";

import Link from "next/link";
import { Mail } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import * as billingService from "@/services/billingService";
import type { BillingPlan, Subscription } from "@/services/billingService";

const ENTERPRISE_EMAIL = "enterprise@sanad.qa";

export function BillingSettings() {
  const { t } = useTranslations();
  const { accessToken } = useAuth();
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);

  useEffect(() => {
    void billingService.listPlans().then(setPlans);
    if (!accessToken) return;
    void billingService.getSubscription(accessToken).then(setSubscription);
  }, [accessToken]);

  return (
    <Card className="glass-card border-border/50">
      <CardHeader>
        <CardTitle className="text-base">{t("billing.title")}</CardTitle>
        <p className="text-xs text-muted-foreground">{t("billing.subtitle")}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {subscription && (
          <div className="rounded-xl border border-border/50 bg-muted/20 p-4">
            <p className="text-sm font-medium">
              {t("billing.currentPlan")}:{" "}
              <span className="text-cyan-400">{t(`billing.tiers.${subscription.tier}`)}</span>
            </p>
            {subscription.queries_limit !== null && (
              <p className="mt-1 text-xs text-muted-foreground">
                {subscription.queries_used} / {subscription.queries_limit} {t("billing.queriesThisMonth")}
              </p>
            )}
          </div>
        )}

        <div className="grid gap-3 md:grid-cols-2">
          {plans.map((plan) => {
            const isCurrent = subscription?.tier === plan.id;
            return (
              <div
                key={plan.id}
                className={`rounded-xl border p-4 ${
                  plan.id === "free" ? "border-cyan-500/30 bg-cyan-500/5" : "border-border/50"
                }`}
              >
                <p className="font-medium">{plan.name}</p>
                <p className="mt-1 text-lg font-bold text-cyan-400">{plan.price_label}</p>
                <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
                  {plan.features.map((feature) => (
                    <li key={feature}>✓ {feature}</li>
                  ))}
                </ul>
                {plan.id === "enterprise" ? (
                  <Button type="button" variant="outline" size="sm" className="mt-4 w-full gap-2" asChild>
                    <a href={`mailto:${ENTERPRISE_EMAIL}`}>
                      <Mail className="h-4 w-4" />
                      {t("billing.contactSales")}
                    </a>
                  </Button>
                ) : isCurrent ? (
                  <p className="mt-4 text-xs text-muted-foreground">{t("billing.current")}</p>
                ) : null}
              </div>
            );
          })}
        </div>

        <p className="text-xs text-muted-foreground">{t("billing.noPaymentNote")}</p>
      </CardContent>
    </Card>
  );
}
