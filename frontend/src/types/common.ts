export type Locale = "ar" | "en";

export type QueryStatus = "pending" | "processing" | "completed" | "failed";

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
