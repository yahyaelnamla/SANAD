import { apiRequest } from "@/services/apiClient";
import type { AuthProvider, TokenResponse, UseCaseChoice } from "@/types/auth";

export interface SsoProvider {
  id: AuthProvider;
  name: string;
  enabled: boolean;
  demo_mode: boolean;
}

export interface SsoStartResponse {
  provider: string;
  mode: string;
  session_id: string | null;
  authorization_url: string | null;
}

export interface SsoCompleteResponse extends TokenResponse {
  is_new_user: boolean;
}

export interface OnboardingStatus {
  completed: boolean;
  use_case: UseCaseChoice | null;
}

export async function listSsoProviders(): Promise<SsoProvider[]> {
  return apiRequest<SsoProvider[]>("/auth/sso/providers");
}

export async function startSso(provider: "google" | "microsoft"): Promise<SsoStartResponse> {
  return apiRequest<SsoStartResponse>("/auth/sso/start", {
    method: "POST",
    body: JSON.stringify({
      provider,
      redirect_uri:
        typeof window !== "undefined"
          ? `${window.location.origin}/auth/sso/callback`
          : undefined,
    }),
  });
}

export async function completeSso(payload: {
  provider: "google" | "microsoft";
  session_id?: string;
  code?: string;
  email?: string;
}): Promise<SsoCompleteResponse> {
  return apiRequest<SsoCompleteResponse>("/auth/sso/complete", {
    method: "POST",
    body: JSON.stringify({
      ...payload,
      redirect_uri:
        typeof window !== "undefined"
          ? `${window.location.origin}/auth/sso/callback`
          : undefined,
    }),
  });
}

export async function getOnboardingStatus(accessToken: string): Promise<OnboardingStatus> {
  return apiRequest<OnboardingStatus>("/auth/me/onboarding", { accessToken });
}

export async function updateOnboarding(
  accessToken: string,
  payload: {
    display_name?: string;
    locale?: "ar" | "en";
    preferred_madhhab?: string;
    favorite_scholars?: string[];
    use_case?: UseCaseChoice;
    completed?: boolean;
  },
): Promise<OnboardingStatus> {
  return apiRequest<OnboardingStatus>("/auth/me/onboarding", {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}
