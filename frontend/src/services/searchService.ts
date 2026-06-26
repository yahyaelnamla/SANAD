import { apiRequest } from "@/services/apiClient";

export interface SearchResultItem {
  type: "chat" | "source" | "scholar" | "company" | "document";
  id: string;
  title: string;
  subtitle?: string | null;
  href: string;
  score?: number;
}

export interface GlobalSearchResponse {
  query: string;
  results: SearchResultItem[];
  total: number;
}

export async function globalSearch(
  accessToken: string,
  query: string,
  limit = 20,
): Promise<GlobalSearchResponse> {
  const encoded = encodeURIComponent(query.trim());
  return apiRequest<GlobalSearchResponse>(`/search?q=${encoded}&limit=${limit}`, {
    accessToken,
  });
}
