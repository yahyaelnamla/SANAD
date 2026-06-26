import { apiRequest } from "@/services/apiClient";

export interface TranscribeResult {
  text: string;
  model: string;
}

export async function transcribeAudio(
  blob: Blob,
  accessToken: string,
  language?: "ar" | "en",
): Promise<TranscribeResult> {
  const formData = new FormData();
  formData.append("file", blob, "recording.webm");
  if (language) {
    formData.append("language", language);
  }

  const { API_BASE_URL, API_PREFIX } = await import("@/lib/constants");
  const url = `${API_BASE_URL}${API_PREFIX}/tools/transcribe`;

  const response = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Voice transcription failed");
  }

  return response.json() as Promise<TranscribeResult>;
}
