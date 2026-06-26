import { apiRequest } from "@/services/apiClient";
import type { SubscriptionTier } from "@/types/auth";

export interface BillingPlan {
  id: string;
  name: string;
  price_label: string;
  price_cents: number | null;
  interval: string | null;
  features: string[];
  recommended: boolean;
}

export interface Subscription {
  tier: SubscriptionTier;
  status: string;
  queries_limit: number | null;
  queries_used: number;
  renews_at: string | null;
}

export interface CheckoutResponse {
  session_id: string;
  mode: string;
  checkout_url: string | null;
  tier: string;
}

export async function listPlans(): Promise<BillingPlan[]> {
  return apiRequest<BillingPlan[]>("/billing/plans");
}

export async function getSubscription(accessToken: string): Promise<Subscription> {
  return apiRequest<Subscription>("/billing/subscription", { accessToken });
}

export async function startCheckout(
  accessToken: string,
  tier: "pro" | "enterprise",
): Promise<CheckoutResponse> {
  return apiRequest<CheckoutResponse>("/billing/checkout", {
    method: "POST",
    accessToken,
    body: JSON.stringify({ tier }),
  });
}

export async function confirmCheckout(
  accessToken: string,
  sessionId: string,
): Promise<{ tier: string; status: string; message: string }> {
  return apiRequest("/billing/checkout/confirm", {
    method: "POST",
    accessToken,
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function cancelSubscription(accessToken: string): Promise<Subscription> {
  return apiRequest<Subscription>("/billing/cancel", {
    method: "POST",
    accessToken,
  });
}
