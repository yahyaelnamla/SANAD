import { apiRequest } from "@/services/apiClient";

export interface ScholarListItem {
  slug: string;
  name: string;
  name_ar?: string | null;
  name_en?: string | null;
  institution: string | null;
  expertise: string[];
  source_count: number;
  is_seed: boolean;
}

export interface ScholarSource {
  id: string;
  title: string;
  source_type: string;
  citation_hint: string | null;
}

export interface ScholarOpinionSample {
  position: string;
  question_context: string | null;
  date: string | null;
  citations: string[];
}

export interface ScholarProfile {
  slug: string;
  name: string;
  name_ar?: string | null;
  name_en?: string | null;
  institution: string | null;
  bio: string | null;
  bio_ar?: string | null;
  expertise: string[];
  source_count: number;
  sources: ScholarSource[];
  opinion_samples: ScholarOpinionSample[];
}

export interface ScholarListResponse {
  items: ScholarListItem[];
  total: number;
}

export async function listScholars(
  accessToken: string,
  query?: string,
): Promise<ScholarListResponse> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("q", query.trim());
  const qs = params.toString();
  return apiRequest<ScholarListResponse>(`/scholars${qs ? `?${qs}` : ""}`, { accessToken });
}

export async function getScholar(accessToken: string, slug: string): Promise<ScholarProfile> {
  return apiRequest<ScholarProfile>(`/scholars/${encodeURIComponent(slug)}`, { accessToken });
}
