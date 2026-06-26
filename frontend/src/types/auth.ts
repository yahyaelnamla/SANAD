export type UserRole = "user" | "admin" | "reviewer";
export type SubscriptionTier = "free" | "pro" | "enterprise";
export type SubscriptionStatus = "active" | "trialing" | "canceled" | "past_due";
export type AuthProvider = "email" | "google" | "microsoft";
export type UseCaseChoice = "personal" | "student" | "professional" | "institution";

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  locale: string;
  subscription_tier: SubscriptionTier;
  subscription_status: SubscriptionStatus;
  onboarding_completed: boolean;
  auth_provider: AuthProvider;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
  locale?: "ar" | "en";
}

export interface LoginPayload {
  email: string;
  password: string;
}
