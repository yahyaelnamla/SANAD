import type { QueryResult, SourceReference } from "@/types/query";

export interface UnifiedSource {
  source: SourceReference;
  excerpts: string[];
}

export function buildUnifiedSources(result: QueryResult): UnifiedSource[] {
  const map = new Map<string, UnifiedSource>();

  for (const source of result.sources) {
    map.set(source.source_id, { source, excerpts: [] });
  }

  for (const item of result.evidence) {
    const existing = map.get(item.source_id);
    if (existing) {
      if (!existing.excerpts.includes(item.text)) {
        existing.excerpts.push(item.text);
      }
      if (!existing.source.source_url && item.metadata?.source_url) {
        existing.source = {
          ...existing.source,
          source_url: String(item.metadata.source_url),
        };
      }
      continue;
    }

    map.set(item.source_id, {
      source: {
        source_id: item.source_id,
        title: item.source_title,
        author: item.source_author,
        type: item.source_type,
        citation: item.citation,
        source_url: item.metadata?.source_url ? String(item.metadata.source_url) : undefined,
      },
      excerpts: [item.text],
    });
  }

  return Array.from(map.values());
}
