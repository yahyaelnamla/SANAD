/** Strip internal model artifacts and escape user-facing text for safe rendering. */

const THINKING_TAG_PATTERN = /<(?:thinking|redacted_thinking)>[\s\S]*?<\/(?:thinking|redacted_thinking)>/gi;
const UNCLOSED_THINKING_PATTERN = /<(?:thinking|redacted_thinking)>[\s\S]*$/i;
const THINKING_HEADER_PATTERN = /^\[Thinking[^\]]*\]\s*/im;
const MODEL_TAG_PATTERN = /<\/?(?:think|thinking|redacted_thinking|assistant|user|system|tool)[^>]*>/gi;
const JSON_BLOCK_PATTERN = /```(?:json)?[\s\S]*?```/gi;
const HTML_TAG_PATTERN = /<[^>]+>/g;
const JSON_LEAK_PATTERN = /\{[\s\S]*?"analysis"[\s\S]*?\}/g;
const PLANNING_LINE_PATTERN =
  /^(?:The user|The question|Let me|I need to|First,|Next,|Now,|For adilla|These form|Moving to|I should|I will|Double-check|Specifically,).*$/gim;

function extractAnalysisFromJsonLeak(text: string): string | null {
  const match = text.match(/"analysis"\s*:\s*"((?:\\.|[^"\\])*)"/);
  if (!match) return null;
  try {
    return JSON.parse(`"${match[1]}"`) as string;
  } catch {
    return match[1].replace(/\\n/g, "\n").replace(/\\"/g, '"').trim() || null;
  }
}

export function sanitizeReasoningForDisplay(text: string | null | undefined): string {
  return sanitizeUserFacingText(text);
}

export function sanitizeUserFacingText(text: string | null | undefined): string {
  if (!text?.trim()) return "";

  const jsonAnalysis = extractAnalysisFromJsonLeak(text);
  if (jsonAnalysis) {
    return sanitizeUserFacingText(jsonAnalysis);
  }

  let cleaned = text.replace(THINKING_TAG_PATTERN, "").replace(MODEL_TAG_PATTERN, "").trim();
  cleaned = cleaned.replace(UNCLOSED_THINKING_PATTERN, "").trim();
  cleaned = cleaned.replace(THINKING_HEADER_PATTERN, "").trim();
  cleaned = cleaned.replace(JSON_BLOCK_PATTERN, "").trim();
  cleaned = cleaned.replace(JSON_LEAK_PATTERN, "").trim();
  cleaned = cleaned.replace(PLANNING_LINE_PATTERN, "").trim();
  cleaned = cleaned.replace(HTML_TAG_PATTERN, "").trim();
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n").trim();

  if (cleaned.startsWith("{") && cleaned.includes('"analysis"')) {
    const nested = extractAnalysisFromJsonLeak(cleaned);
    if (nested) return sanitizeUserFacingText(nested);
    return "";
  }

  return cleaned;
}

export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Sanitize then escape for plain-text React rendering (never use dangerouslySetInnerHTML). */
export function toSafeDisplayText(text: string | null | undefined): string {
  return escapeHtml(sanitizeUserFacingText(text));
}
