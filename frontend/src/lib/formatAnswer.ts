/** Parse and clean user-facing answer text for rich rendering. */



const SUMMARY_SEPARATOR = /━━━/;

const SUMMARY_LABEL = /^(?:خلاصة|In short)\s*:?\s*$/i;



const URL_PATTERN = /https?:\/\/[^\s]+/gi;

const MARKDOWN_LINK_PATTERN = /\[([^\]]*)\]\([^)]+\)/g;

const NUMBERED_REF_PATTERN = /\s*\(\d{1,3}\)/g;

const BRACKET_REF_PATTERN = /\s*\[[\d\u0660-\u0669,\s؛،]+\]/g;

const ARTIFACT_PATTERN = /\bnbs\b|&nbsp;|&#160;/gi;

const INLINE_CITATION_PATTERN =

  /(?:\s*[\[(]?)(?:Surah|سورة|S\.|ص\.)\s*[^\])]+[\])]?|\s*\([^)]*(?:نسائي|بخاري|مسلم|ترمذي|أبو داود|ابن ماجه|Bukhari|Muslim|Nasai|Tirmidhi|Abu Dawud|Ibn Majah)[^)]*\)/gi;



const VERSE_BLOCK_PATTERN = /﴿[^﴾]+﴾/g;

const HADITH_MARKERS =

  /قال\s*رسول\s*الله|صلى\s*الله\s*عليه\s*وسلم|عن\s+[\u0600-\u06FF]+\s*رضي|رو[ىي]\s|Hadith|حديث\s*نبو/i;



export type ParagraphKind = "text" | "quran" | "hadith" | "section-label";



export interface AnswerSection {

  body: string;

  summary: string | null;

}



export interface FormattedParagraph {

  kind: ParagraphKind;

  text: string;

}



export function splitAnswerSections(text: string): AnswerSection {

  const cleaned = text.trim();

  if (!SUMMARY_SEPARATOR.test(cleaned)) {

    return { body: cleaned, summary: null };

  }



  const parts = cleaned.split(SUMMARY_SEPARATOR);

  const body = parts[0]?.trim() ?? "";

  const tail = parts.slice(1).join("━━━").trim();

  const tailLines = tail.split("\n").map((l) => l.trim()).filter(Boolean);

  const summaryLines = tailLines.filter((line) => !SUMMARY_LABEL.test(line));

  const summary = summaryLines.join("\n").trim() || null;



  return { body, summary };

}



function collapseHorizontalSpaces(text: string): string {

  return text

    .split("\n")

    .map((line) => line.replace(/[ \t]{2,}/g, " ").trimEnd())

    .join("\n")

    .replace(/\n{3,}/g, "\n\n");

}



export function stripInlineCitations(text: string): string {

  return collapseHorizontalSpaces(

    text

      .replace(ARTIFACT_PATTERN, " ")

      .replace(MARKDOWN_LINK_PATTERN, "$1")

      .replace(URL_PATTERN, "")

      .replace(BRACKET_REF_PATTERN, "")

      .replace(NUMBERED_REF_PATTERN, "")

      .replace(INLINE_CITATION_PATTERN, ""),

  ).trim();

}



function classifyParagraph(text: string): ParagraphKind {

  const trimmed = text.trim();

  if (!trimmed) return "text";



  if (
    /^(?:الحكم|النتيجة|Conclusion|Key evidence|Scholarly views|Practical note|الأدلة|الرأي|ملاحظة|تعريف|من الكتاب|من السنة|من الإجماع|من كلام العلماء|الحكمة|From the Quran|From the Sunnah|From consensus|From scholars)\s*:?$/i.test(
      trimmed,
    ) ||
    /^(?:من الكتاب|من السنة|من الإجماع|من كلام العلماء|الحكمة من)/.test(trimmed)
  ) {

    return "section-label";

  }



  if (HADITH_MARKERS.test(trimmed) && trimmed.length < 900) {

    return "hadith";

  }



  return "text";

}



function splitBodyIntoBlocks(body: string): string[] {

  const byParagraph = body.split(/\n{2,}/).map((b) => b.trim()).filter(Boolean);

  if (byParagraph.length > 1) return byParagraph;



  const byLine = body.split(/\n/).map((l) => l.trim()).filter(Boolean);

  if (byLine.length > 1) return byLine;



  return [body.trim()];

}



function splitMixedContent(text: string): FormattedParagraph[] {

  const parts: FormattedParagraph[] = [];

  let lastIndex = 0;

  let match: RegExpExecArray | null;



  VERSE_BLOCK_PATTERN.lastIndex = 0;

  while ((match = VERSE_BLOCK_PATTERN.exec(text)) !== null) {

    if (match.index > lastIndex) {

      const before = text.slice(lastIndex, match.index).trim();

      if (before) {

        splitBodyIntoBlocks(before).forEach((block) => {

          parts.push({ kind: classifyParagraph(block), text: block });

        });

      }

    }

    parts.push({ kind: "quran", text: match[0].trim() });

    lastIndex = match.index + match[0].length;

  }



  const rest = text.slice(lastIndex).trim();

  if (rest) {

    splitBodyIntoBlocks(rest).forEach((block) => {

      parts.push({ kind: classifyParagraph(block), text: block });

    });

  }



  return parts;

}



export function parseAnswerParagraphs(text: string): FormattedParagraph[] {

  const { body } = splitAnswerSections(text);

  const cleaned = stripInlineCitations(body);



  if (cleaned.includes("﴿") && cleaned.includes("﴾")) {

    const mixed = splitMixedContent(cleaned);

    if (mixed.length > 0) return mixed;

  }



  return splitBodyIntoBlocks(cleaned).map((block) => ({

    kind: classifyParagraph(block),

    text: block,

  }));

}

