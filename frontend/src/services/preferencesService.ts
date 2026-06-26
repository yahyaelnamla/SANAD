import { apiRequest } from "@/services/apiClient";

export type MadhhabChoice = "hanafi" | "maliki" | "shafii" | "hanbali" | "general";

export interface SavedBookmark {
  query_id: string;
  question: string;
  summary?: string | null;
  note?: string | null;
  folder?: string | null;
  is_favorite?: boolean;
  saved_at?: string | null;
}

export interface SavedPortfolioHolding {
  symbol: string;
  quantity: number;
  asset_type: "stock" | "crypto" | "etf" | "fund" | "reit";
  purchase_price?: number | null;
  manual_price?: number | null;
  use_market_price?: boolean;
}

export interface SavedPortfolioProfile {
  id: string;
  name: string;
  holdings: SavedPortfolioHolding[];
  created_at: string;
  last_scanned_at?: string | null;
}

export interface UserPreferences {
  display_name: string | null;
  preferred_madhhab: MadhhabChoice | null;
  favorite_scholars: string[];
  saved_companies: string[];
  saved_portfolios: string[];
  saved_portfolio_profiles: SavedPortfolioProfile[];
  recent_topics: string[];
  bookmarks: SavedBookmark[];
}

export type UserPreferencesUpdate = Partial<UserPreferences>;

export async function getUserPreferences(accessToken: string): Promise<UserPreferences> {
  return apiRequest<UserPreferences>("/auth/me/preferences", { accessToken });
}

export async function updateUserPreferences(
  accessToken: string,
  payload: UserPreferencesUpdate,
): Promise<UserPreferences> {
  return apiRequest<UserPreferences>("/auth/me/preferences", {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}
