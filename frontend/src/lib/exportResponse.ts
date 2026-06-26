import type { QueryResult } from "@/types/query";

function section(title: string, body: string): string {
  if (!body.trim()) return "";
  return `## ${title}\n\n${body.trim()}\n\n`;
}

export function buildMarkdownExport(result: QueryResult): string {
  const lines: string[] = [
    `# SANAD — ${result.question}`,
    "",
    `_Generated ${new Date(result.created_at).toLocaleString()}_`,
    "",
  ];

  if (result.summary) {
    lines.push(section("Summary", result.summary));
  }

  if (result.evidence.length > 0) {
    const evidenceBody = result.evidence
      .map(
        (item, index) =>
          `### Evidence ${index + 1}\n${item.text}\n\n**Citation:** ${item.citation}\n**Source:** ${item.source_author} — ${item.source_title}`,
      )
      .join("\n\n");
    lines.push(section("Evidence", evidenceBody));
  }

  if (result.reasoning) {
    lines.push(section("Jurisprudential Analysis", result.reasoning));
  }

  if (result.opinions.length > 0) {
    const opinionsBody = result.opinions
      .map((opinion) => {
        const meta = [
          opinion.book && `Book: ${opinion.book}`,
          opinion.fatwa && `Fatwa: ${opinion.fatwa}`,
          opinion.page && `Page: ${opinion.page}`,
          opinion.standard && `Standard: ${opinion.standard}`,
          opinion.section && `Section: ${opinion.section}`,
          opinion.date && `Date: ${opinion.date}`,
        ]
          .filter(Boolean)
          .join("; ");
        return `- **${opinion.scholar}**${opinion.institution ? ` (${opinion.institution})` : ""}: ${opinion.position}${meta ? `\n  _${meta}_` : ""}`;
      })
      .join("\n");
    lines.push(section("Scholarly Opinions", opinionsBody));
  }

  if (result.madhhab_matrix && result.madhhab_matrix.length > 0) {
    const matrixBody = result.madhhab_matrix
      .map((row) => `- **${row.school}** (${row.alignment}): ${row.position}`)
      .join("\n");
    lines.push(section("Madhhab Matrix", matrixBody));
  }

  if (result.financial_context?.screening_notes?.length) {
    lines.push(
      section("Financial Screening", result.financial_context.screening_notes.join("\n- ")),
    );
  }

  if (result.sources.length > 0) {
    const sourcesBody = result.sources
      .map((source) => `- ${source.author} — ${source.title} (${source.citation})`)
      .join("\n");
    lines.push(section("Sources", sourcesBody));
  }

  return lines.join("\n").trim();
}

export function downloadMarkdown(result: QueryResult): void {
  const markdown = buildMarkdownExport(result);
  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `sanad-${result.query_id.slice(0, 8)}.md`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function downloadPdf(result: QueryResult): void {
  const markdown = buildMarkdownExport(result);
  const htmlBody = markdown
    .split("\n")
    .map((line) => {
      if (line.startsWith("# ")) return `<h1>${escapeHtml(line.slice(2))}</h1>`;
      if (line.startsWith("## ")) return `<h2>${escapeHtml(line.slice(3))}</h2>`;
      if (line.startsWith("### ")) return `<h3>${escapeHtml(line.slice(4))}</h3>`;
      if (line.startsWith("- ")) return `<li>${escapeHtml(line.slice(2))}</li>`;
      if (!line.trim()) return "<br/>";
      return `<p>${escapeHtml(line)}</p>`;
    })
    .join("\n");

  const printWindow = window.open("", "_blank", "noopener,noreferrer,width=800,height=900");
  if (!printWindow) return;

  printWindow.document.write(`<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>SANAD Export</title>
<style>
  body { font-family: Georgia, serif; padding: 2rem; color: #111; line-height: 1.5; }
  h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
  h2 { font-size: 1.1rem; margin-top: 1.25rem; color: #0d4f6e; }
  p, li { font-size: 0.95rem; }
</style></head><body>${htmlBody}</body></html>`);
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
}
