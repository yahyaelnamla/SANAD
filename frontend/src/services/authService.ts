import { apiRequest } from "@/services/apiClient";
import type { LoginPayload, RegisterPayload, TokenResponse, UserProfile } from "@/types/auth";

export async function register(payload: RegisterPayload): Promise<UserProfile> {
  return apiRequest<UserProfile>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getProfile(accessToken: string): Promise<UserProfile> {
  return apiRequest<UserProfile>("/auth/me", {
    accessToken,
  });
}
