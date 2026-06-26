import type { Locale } from "@/types/common";

type LocalizedMap = Record<string, { ar: string; en: string }>;

const AGENT_STEPS: LocalizedMap = {
  Planner: { ar: "تخطيط التنفيذ", en: "Execution Planning" },
  IntentAgent: { ar: "تحليل النية", en: "Intent Analysis" },
  RetrievalAgent: { ar: "استرجاع الأدلة", en: "Evidence Retrieval" },
  KnowledgeAgent: { ar: "تجميع المعرفة", en: "Knowledge Synthesis" },
  FinancialContextAgent: { ar: "السياق المالي", en: "Financial Context" },
  DocumentMemory: { ar: "ذاكرة المستندات", en: "Document Memory" },
  ReasoningAgent: { ar: "الاستدلال الفقهي", en: "Fiqh Reasoning" },
  VerificationAgent: { ar: "التحقق والحماية", en: "Verification & Guard" },
  ResponseBuilder: { ar: "بناء الإجابة", en: "Response Builder" },
};

const TRACE_STATUS: LocalizedMap = {
  completed: { ar: "مكتمل", en: "completed" },
  running: { ar: "جاري", en: "running" },
  rejected: { ar: "مرفوض", en: "rejected" },
  pending: { ar: "انتظار", en: "pending" },
};

const FANAR_CAPABILITIES: LocalizedMap = {
  "Fanar-Sadiq": {
    ar: "إجابات عامة، توليد عربي، ملخصات، استجابات سريعة، استرجاع RAG",
    en: "General answers, Arabic generation, summaries, fast responses, RAG retrieval",
  },
  "Fanar-Sadiq-Agentic": {
    ar: "تخطيط خط أنابيب متعدد الوكلاء وتنسيق الأدوات",
    en: "Multi-agent pipeline planning and tool orchestration",
  },
  "Fanar-C-2-27B": {
    ar: "استدلال معقد، مقارنات، خلافات فتوى، تركيب متعدد الخطوات",
    en: "Complex reasoning, comparisons, fatwa disagreements, multi-step synthesis",
  },
  "Fanar-Guard-2": {
    ar: "تحقق إلزامي — لا يُتجاوز أبداً؛ يرفض عند انقطاع API",
    en: "Mandatory verification — never bypassed; fail-closed on API outage",
  },
  "Fanar-Aura-STT-1": {
    ar: "محادثات صوتية، لهجات عربية، تحويل كلام إلى نص",
    en: "Voice conversations, Arabic dialects, speech-to-text",
  },
  "Fanar-Oryx-IVU-2": {
    ar: "OCR للPDF، جداول، تقارير مالية، مستندات ممسوحة",
    en: "PDF OCR, tables, financial reports, scanned documents",
  },
  "Fanar-Shaheen-MT-1": {
    ar: "ترجمة ثنائية اللغة ومتعددة اللغات",
    en: "Bilingual and multilingual translation",
  },
};

const FANAR_IMPROVEMENTS: LocalizedMap = {
  "Fanar-Sadiq": {
    ar: "بث رموز SSE أصلي سيقلل زمن الاستجابة المحسوس في المحادثة",
    en: "Native SSE token streaming would reduce perceived latency in chat",
  },
  "Fanar-Sadiq-Agentic": {
    ar: "مخطط استدعاء أدوات منظم لـ Yahoo Finance و Serper يبسّط التنسيق",
    en: "Structured tool-call schema for Yahoo Finance / Serper would simplify orchestration",
  },
  "Fanar-C-2-27B": {
    ar: "مخطط JSON فقهي عربي مخصص لمصفوفات المذاهب وآراء العلماء",
    en: "Dedicated Arabic fiqh JSON schema for madhhab matrices and opinion objects",
  },
  "Fanar-Guard-2": {
    ar: "نقطة نهاية للتحقق الدفعي للإجابات متعددة الأقسام",
    en: "Batch moderation endpoint for multi-section responses (summary + analysis)",
  },
  "Fanar-Aura-STT-1": {
    ar: "نسخ جزئي فوري أثناء الأسئلة الشرعية الطويلة",
    en: "Real-time partial transcripts during long-form scholarly questions",
  },
  "Fanar-Oryx-IVU-2": {
    ar: "وضع استخراج جداول مُحسّن لتقارير المعايير الشرعية السنوية",
    en: "Table extraction mode tuned for Shariah standards annual report layouts",
  },
  "Fanar-Shaheen-MT-1": {
    ar: "الحفاظ على مراجع القرآن والحديث عند ترجمة الإجابات",
    en: "Preserve inline Quran/Hadith citations when translating answers",
  },
};

const EVALUATION_DEMOS: Record<string, { title: LocalizedMap[string]; description: LocalizedMap[string] }> = {
  fast_riba: {
    title: { ar: "إجابة شرعية سريعة", en: "Fast Shariah answer" },
    description: {
      ar: "سؤال فقهي بسيط عبر الاسترجاع + Fanar-Sadiq في ثوانٍ",
      en: "Simple fiqh question routed through retrieval + Fanar-Sadiq in seconds",
    },
  },
  deep_bitcoin: {
    title: { ar: "تحليل متعدد العلماء", en: "Deep multi-scholar analysis" },
    description: {
      ar: "مقارنة معقدة عبر Fanar-C-2-27B مع تحقق Fanar-Guard-2",
      en: "Complex comparison uses Fanar-C-2-27B reasoning with Guard verification",
    },
  },
  company_scan: {
    title: { ar: "فحص شركات شرعي", en: "Company Shariah screening" },
    description: {
      ar: "سياق مالي حي مع Fanar-Sadiq وبيانات السوق",
      en: "Live financial context with Fanar-Sadiq synthesis and market data",
    },
  },
  document_ocr: {
    title: { ar: "تحليل PDF و OCR", en: "PDF & OCR analysis" },
    description: {
      ar: "ارفع تقارير — Fanar-Oryx-IVU يستخرج الجداول ومؤشرات الربا",
      en: "Upload annual reports — Fanar-Oryx-IVU extracts tables and riba signals",
    },
  },
  voice_ar: {
    title: { ar: "مساعد صوتي", en: "Voice assistant" },
    description: {
      ar: "سجّل بالعربية أو الإنجليزية — Fanar-Aura-STT-1 ينسخ بدعم اللهجات",
      en: "Record in Arabic or English — Fanar-Aura-STT-1 transcribes with dialect support",
    },
  },
  translate: {
    title: { ar: "إجابات متعددة اللغات", en: "Multilingual answers" },
    description: {
      ar: "ترجمة فورية عبر Fanar-Shaheen-MT-1 دون إعادة تشغيل خط الأنابيب",
      en: "Instant translation via Fanar-Shaheen without rerunning the pipeline",
    },
  },
};

const FEATURE_MATRIX: Record<string, { feature: LocalizedMap[string]; description: LocalizedMap[string] }> = {
  chat: {
    feature: { ar: "المحادثة والملخصات", en: "Chat & summaries" },
    description: {
      ar: "نية، تركيب معرفة، بناء إجابة، أسئلة متابعة",
      en: "Intent, knowledge synthesis, response building, follow-ups",
    },
  },
  deep_fiqh: {
    feature: { ar: "استدلال فقهي عميق", en: "Deep fiqh reasoning" },
    description: {
      ar: "مقارنات، خلافات، تركيب متعدد الخطوات مع حماية إلزامية",
      en: "Comparisons, disagreements, multi-step synthesis with mandatory guard",
    },
  },
  evidence: {
    feature: { ar: "استرجاع الأدلة", en: "Evidence retrieval" },
    description: {
      ar: "RAG على قرآن وحديث وفتاوى ومعايير شرعية موثقة",
      en: "RAG over authenticated Quran, Hadith, fatwa, and Shariah standards",
    },
  },
  voice: {
    feature: { ar: "الوضع الصوتي", en: "Voice mode" },
    description: {
      ar: "لهجات عربية وتحويل كلام إلى نص في المحادثة",
      en: "Arabic dialects and English speech-to-text in chat",
    },
  },
  documents: {
    feature: { ar: "محلل المستندات", en: "Document analyzer" },
    description: {
      ar: "OCR، جداول، كشف ربا، أسئلة متابعة على المستندات",
      en: "OCR, tables, riba detection, document-memory Q&A",
    },
  },
  translation: {
    feature: { ar: "الترجمة", en: "Translation" },
    description: {
      ar: "ترجمة الإجابات لست لغات مع الحفاظ على المراجع",
      en: "Six-language answer translation preserving citations",
    },
  },
};

const EXPERTISE_TAGS: LocalizedMap = {
  AAOIFI: { ar: "معايير AAOIFI", en: "AAOIFI standards" },
  stocks: { ar: "الأسهم", en: "Equities" },
  sukuk: { ar: "الصكوك", en: "Sukuk" },
  banking: { ar: "المصرفية الإسلامية", en: "Islamic banking" },
  fiqh: { ar: "الفقه", en: "Fiqh" },
  "contemporary fatwa": { ar: "فتاوى معاصرة", en: "Contemporary fatwa" },
  international: { ar: "دولي", en: "International" },
  Hanafi: { ar: "الحنفي", en: "Hanafi" },
  murabaha: { ar: "المرابحة", en: "Murabaha" },
  zakat: { ar: "الزكاة", en: "Zakat" },
  "commercial law": { ar: "القانون التجاري", en: "Commercial law" },
  standards: { ar: "المعايير الشرعية", en: "Shariah standards" },
  fatwa: { ar: "فتوى", en: "Fatwa" },
  quran: { ar: "قرآن", en: "Quran" },
  hadith: { ar: "حديث", en: "Hadith" },
  standard: { ar: "معيار", en: "Standard" },
  fiqh_reference: { ar: "مرجع فقهي", en: "Fiqh reference" },
};

const GRAPH_NODES: LocalizedMap = {
  quran: { ar: "القرآن الكريم", en: "Quran" },
  hadith: { ar: "الحديث النبوي", en: "Hadith" },
  aaoifi: { ar: "AAOIFI", en: "AAOIFI" },
  fiqh_academy: { ar: "مجمع الفقه الإسلامي الدولي", en: "International Fiqh Academy" },
  riba: { ar: "الربا", en: "Riba" },
  stocks: { ar: "الأسهم", en: "Equities" },
  zakat: { ar: "الزكاة", en: "Zakat" },
  sukuk: { ar: "الصكوك", en: "Sukuk" },
  murabaha: { ar: "المرابحة", en: "Murabaha" },
  crypto: { ar: "العملات الرقمية / DeFi", en: "Crypto / DeFi" },
  listed_equity: { ar: "شركة مدرجة", en: "Listed company" },
};

const GRAPH_EDGES: LocalizedMap = {
  prohibits: { ar: "يحرّم", en: "prohibits" },
  warns: { ar: "ينذر", en: "warns" },
  screens: { ar: "يفحص", en: "screens" },
  guidance: { ar: "يرشد", en: "guidance" },
  standards: { ar: "معايير", en: "standards" },
  mandates: { ar: "يفرض", en: "mandates" },
  reviews: { ar: "يراجع", en: "reviews" },
  related: { ar: "مرتبط", en: "related" },
  references: { ar: "يستشهد", en: "references" },
};

const GRAPH_NODE_TYPES: LocalizedMap = {
  quran: { ar: "قرآن", en: "Quran" },
  hadith: { ar: "حديث", en: "Hadith" },
  standard: { ar: "معيار", en: "Standard" },
  institution: { ar: "مؤسسة", en: "Institution" },
  topic: { ar: "موضوع", en: "Topic" },
  concept: { ar: "مفهوم", en: "Concept" },
  company: { ar: "شركة", en: "Company" },
  classical: { ar: "كلاسيكي", en: "Classical" },
  fatwa: { ar: "فتوى", en: "Fatwa" },
  entity: { ar: "كيان", en: "Entity" },
};

const PIPELINE_DEPTH: LocalizedMap = {
  fast: { ar: "سريع", en: "fast" },
  deep: { ar: "معمّق", en: "deep" },
  standard: { ar: "عادي", en: "standard" },
};

const HARNESS_CATEGORIES: LocalizedMap = {
  fast_answer: { ar: "إجابة سريعة", en: "fast_answer" },
  deep_analysis: { ar: "تحليل عميق", en: "deep_analysis" },
  honesty: { ar: "الصدق", en: "honesty" },
  financial: { ar: "مالي", en: "financial" },
  multilingual: { ar: "متعدد اللغات", en: "multilingual" },
};

const EVAL_LIMITATIONS: Record<number, LocalizedMap[string]> = {
  0: {
    ar: "عدد الرموز يعتمد على بيانات استخدام Fanar عند إرجاعها من API",
    en: "Token counts depend on Fanar usage metadata when returned by the API",
  },
  1: {
    ar: "أسعار السوق الحية قد تتأخر؛ تُستخدم أسعار مخزنة كاحتياط",
    en: "Live market quotes may time out; cached quotes used as fallback",
  },
  2: {
    ar: "آراء العلماء تتطلب مصادر موثقة — تُحذف الادعاءات غير المؤسسة",
    en: "Scholarly opinions require authenticated source grounding — ungrounded claims are dropped",
  },
};

const EVAL_FUTURE: Record<number, LocalizedMap[string]> = {
  0: {
    ar: "بث رموز أصلي من Fanar-Sadiq لتقليل زمن الاستجابة المحسوس",
    en: "Native streaming token events from Fanar-Sadiq for lower perceived latency",
  },
  1: {
    ar: "وضع JSON منظم لمصفوفة المذاهب وحقول الفحص المالي",
    en: "Structured JSON mode for madhhab matrix and financial screening fields",
  },
  2: {
    ar: "API تضمين دفعي لتسريع إدخال قاعدة المعرفة",
    en: "Batch embedding API for faster knowledge-base ingestion",
  },
  3: {
    ar: "استدعاء أدوات أصلي من Fanar-Sadiq-Agentic لـ Yahoo Finance و Serper",
    en: "Fanar-Sadiq-Agentic native tool-call schema for Yahoo Finance and Serper",
  },
  4: {
    ar: "تحقق دفعي من Fanar-Guard-2 للإجابات متعددة الأقسام",
    en: "Fanar-Guard-2 batch moderation for multi-section responses",
  },
};

function pick(entry: LocalizedMap[string] | undefined, locale: Locale, fallback: string): string {
  if (!entry) return fallback;
  return locale === "ar" ? entry.ar : entry.en;
}

export function localizeAgentStep(agent: string, locale: Locale): string {
  return pick(AGENT_STEPS[agent], locale, agent);
}

export function localizeTraceStatus(status: string, locale: Locale): string {
  if (status === "completed") return locale === "ar" ? "✓" : "✓";
  return pick(TRACE_STATUS[status], locale, status);
}

export function localizeFanarCapability(model: string, locale: Locale, fallback: string): string {
  return pick(FANAR_CAPABILITIES[model], locale, fallback);
}

export function localizeFanarImprovement(model: string, locale: Locale, fallback: string): string {
  return pick(FANAR_IMPROVEMENTS[model], locale, fallback);
}

export function localizeEvaluationDemo(
  id: string,
  field: "title" | "description",
  locale: Locale,
  fallback: string,
): string {
  const entry = EVALUATION_DEMOS[id];
  if (!entry) return fallback;
  return pick(entry[field], locale, fallback);
}

export function localizeFeatureMatrix(
  key: string,
  field: "feature" | "description",
  locale: Locale,
  fallback: string,
): string {
  const entry = FEATURE_MATRIX[key];
  if (!entry) return fallback;
  return pick(entry[field], locale, fallback);
}

export function localizeExpertiseTag(tag: string, locale: Locale): string {
  const normalized = tag.trim();
  return pick(EXPERTISE_TAGS[normalized], locale, normalized);
}

export function localizeGraphNode(nodeId: string, label: string, locale: Locale): string {
  const baseId = nodeId.replace(/^source-/, "");
  if (GRAPH_NODES[nodeId]) return pick(GRAPH_NODES[nodeId], locale, label);
  if (GRAPH_NODES[baseId]) return pick(GRAPH_NODES[baseId], locale, label);
  if (nodeId.startsWith("source-")) return label;
  return pick(GRAPH_NODES[nodeId], locale, label);
}

export function localizeGraphEdge(label: string, locale: Locale): string {
  return pick(GRAPH_EDGES[label], locale, label);
}

export function localizeGraphNodeType(type: string, locale: Locale): string {
  return pick(GRAPH_NODE_TYPES[type], locale, type);
}

export function localizePipelineDepth(depth: string, locale: Locale): string {
  return pick(PIPELINE_DEPTH[depth], locale, depth);
}

export function localizeHarnessCategory(category: string, locale: Locale): string {
  return pick(HARNESS_CATEGORIES[category], locale, category);
}

export function localizeEvalLimitation(index: number, locale: Locale, fallback: string): string {
  return pick(EVAL_LIMITATIONS[index], locale, fallback);
}

export function localizeEvalFuture(index: number, locale: Locale, fallback: string): string {
  return pick(EVAL_FUTURE[index], locale, fallback);
}

const HARNESS_QUESTIONS: Record<string, LocalizedMap[string]> = {
  fast_riba: { ar: "هل الربا محرم؟", en: "Is riba haram?" },
  deep_bitcoin: {
    ar: "قارن آراء العلماء في Bitcoin staking ومنتجات العائد.",
    en: "Compare scholarly opinions on Bitcoin staking and yield products.",
  },
  refusal_no_evidence: {
    ar: "ما حكم SANAD-XYZ-9999 synthetic token staking؟",
    en: "What is the ruling on SANAD-XYZ-9999 synthetic token staking?",
  },
  company_screening: {
    ar: "كيف أفحص شركة مدرجة للامتثال الشرعي؟",
    en: "How do I screen a listed company for Shariah compliance?",
  },
  arabic_zakat: { ar: "ما حكم تأخير الزكاة؟", en: "ما حكم تأخير الزكاة؟" },
};

export function localizeHarnessQuestion(caseId: string, locale: Locale, fallback: string): string {
  return pick(HARNESS_QUESTIONS[caseId], locale, fallback);
}

export function localizeScholarInstitution(
  slug: string,
  institution: string,
  locale: Locale,
): string {
  const INSTITUTIONS: Record<string, LocalizedMap[string]> = {
    "aaoifi-shariah-board": {
      ar: "هيئة المحاسبة والمراجعة للمؤسسات المالية الإسلامية",
      en: "Accounting and Auditing Organization for Islamic Financial Institutions",
    },
    "international-islamic-fiqh-academy": {
      ar: "مجمع الفقه الإسلامي الدولي (منظمة التعاون الإسلامي)",
      en: "OIC International Islamic Fiqh Academy",
    },
    "sheikh-muhammad-taqi-usmani": {
      ar: "دار العلوم، باكستان",
      en: "Darul Uloom Karachi",
    },
    "sheikh-yusuf-al-qaradawi": {
      ar: "المجلس الأوروبي للإفتاء والبحوث",
      en: "European Council for Fatwa and Research",
    },
    "sheikh-abdul-sattar-abu-ghuddah": {
      ar: "AAOIFI / مجمع الفقه الإسلامي",
      en: "AAOIFI / Islamic Fiqh Academy",
    },
  };
  return pick(INSTITUTIONS[slug], locale, institution);
}
