import { API_BASE_URL, API_PREFIX } from "@/lib/constants";
import type { ApiError } from "@/types/common";

export class ApiClientError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

interface RequestOptions extends RequestInit {
  accessToken?: string;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { accessToken, headers, ...rest } = options;
  const url = `${API_BASE_URL}${API_PREFIX}${path}`;

  const requestHeaders: HeadersInit = {
    "Content-Type": "application/json",
    ...(headers ?? {}),
  };

  if (accessToken) {
    (requestHeaders as Record<string, string>).Authorization = `Bearer ${accessToken}`;
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...rest,
      headers: requestHeaders,
      cache: rest.cache ?? (rest.method && rest.method !== "GET" ? "default" : "no-store"),
    });
  } catch {
    throw new ApiClientError(0, "NETWORK_ERROR", "Network request failed");
  }

  if (response.ok) {
    if (response.status === 204) {
      return undefined as T;
    }
    return response.json() as Promise<T>;
  }

  let errorBody: ApiError = {
    code: "INTERNAL_ERROR",
    message: response.statusText,
  };

  try {
    errorBody = (await response.json()) as ApiError;
  } catch {
    // keep default
  }

  throw new ApiClientError(
    response.status,
    errorBody.code,
    errorBody.message,
    errorBody.details,
  );
}
