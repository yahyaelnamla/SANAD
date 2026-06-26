import { ApiClientError } from "@/services/apiClient";

export function getAuthErrorMessage(
  error: unknown,
  fallback: string,
  networkFallback: string,
): string {
  if (error instanceof ApiClientError) {
    if (error.code === "NETWORK_ERROR") {
      return networkFallback;
    }
    return error.message || fallback;
  }
  return fallback;
}
