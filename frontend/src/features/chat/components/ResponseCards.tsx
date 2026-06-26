"use client";

import { motion } from "framer-motion";
import { memo, useState } from "react";
import {
  BookOpen,
  FileText,
  Globe,
  Landmark,
  LineChart,
  ScrollText,
  Scale,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CitationChip } from "@/features/chat/components/CitationChip";
import { SourceCardsSection } from "@/features/chat/components/SourceCardsSection";

import { useProgressiveReveal } from "@/hooks/useProgressiveReveal";

import { useTranslations } from "@/hooks/useTranslations";

import { sanitizeReasoningForDisplay } from "@/lib/sanitizeResponse";

import { cn } from "@/lib/utils";

import type { QueryResult } from "@/types/query";



const ALIGNMENT_STYLES: Record<string, string> = {

  agree: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",

  disagree: "bg-destructive/10 text-destructive border-destructive/30",

  mixed: "bg-amber-500/10 text-amber-400 border-amber-500/30",

};



function sourceTypeIcon(type: string) {

  if (type === "fatwa") return FileText;

  if (type === "standard") return Landmark;

  if (type.includes("http")) return Globe;

  return BookOpen;

}



function CitationLink({
  citation,
  url,
  sourceId,
  sourceTitle,
  sourceAuthor,
  snippet,
  onOpenSource,
}: {
  citation: string;
  url?: string | null;
  sourceId?: string;
  sourceTitle?: string;
  sourceAuthor?: string;
  snippet?: string;
  onOpenSource?: (sourceId: string) => void;
}) {
  return (
    <CitationChip
      citation={citation}
      sourceId={sourceId}
      sourceTitle={sourceTitle}
      sourceAuthor={sourceAuthor}
      snippet={snippet}
      url={url}
      onOpenSource={onOpenSource}
    />
  );
}



function RevealSection({

  visible,

  children,

}: {

  visible: boolean;

  children: React.ReactNode;

}) {

  if (!visible) return null;

  return (

    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>

      {children}

    </motion.div>

  );

}



interface ResponseCardsProps {

  result: QueryResult;

  className?: string;

  revealProgressively?: boolean;

}



export const ResponseCards = memo(function ResponseCards({
  result,
  className,
  revealProgressively = false,
}: ResponseCardsProps) {
  const { t, locale } = useTranslations();
  const isArabic = locale === "ar";
  const reasoningText = sanitizeReasoningForDisplay(result.reasoning);
  const { isVisible } = useProgressiveReveal(revealProgressively);
  const [openSourceIds, setOpenSourceIds] = useState<string[]>([]);
  const madhhabMatrix = result.madhhab_matrix ?? [];
  const financial = result.financial_context;

  const hasFinancial =

    Boolean(financial?.has_external_data) ||

    (financial?.screening_notes?.length ?? 0) > 0 ||

    (financial?.market_quotes?.length ?? 0) > 0 ||

    (financial?.entities?.length ?? 0) > 0;



  function openSourcePanel(sourceId: string) {
    setOpenSourceIds((prev) => (prev.includes(sourceId) ? prev : [...prev, sourceId]));
    window.setTimeout(() => {
      document.getElementById(`source-panel-${sourceId}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 80);
  }

  function alignmentLabel(alignment: string): string {
    const key = `responseCards.alignment.${alignment}`;
    const translated = t(key);
    return translated === key ? alignment : translated;
  }



  return (

    <div className={cn("space-y-4", className)}>

      {result.summary && (

        <RevealSection visible={!revealProgressively || isVisible("summary")}>

          <Card className="glass-card border-cyan-500/20">

            <CardHeader className="pb-2">

              <CardTitle className="flex items-center gap-2 text-sm font-semibold text-cyan-300">

                <ScrollText className="h-4 w-4" />

                {t("responseCards.summary")}

              </CardTitle>

            </CardHeader>

            <CardContent className="space-y-3">
              <p className={cn("text-sm leading-relaxed", isArabic && "font-arabic")}>{result.summary}</p>
              {result.evidence.length > 0 && (
                <div className="flex flex-wrap gap-1.5 border-t border-border/30 pt-3">
                  {result.evidence.slice(0, 6).map((item) => (
                    <CitationLink
                      key={`${item.chunk_id}-summary-cite`}
                      citation={item.citation}
                      url={(item.metadata?.source_url as string | undefined) ?? null}
                      sourceId={item.source_id}
                      sourceTitle={item.source_title}
                      sourceAuthor={item.source_author}
                      snippet={item.text}
                      onOpenSource={openSourcePanel}
                    />
                  ))}
                </div>
              )}
            </CardContent>

          </Card>

        </RevealSection>

      )}



      {result.evidence.length > 0 && (

        <RevealSection visible={!revealProgressively || isVisible("evidence")}>

          <Card className="glass-card border-border/50">

            <CardHeader className="pb-2">

              <CardTitle className="flex items-center gap-2 text-sm font-semibold">

                <BookOpen className="h-4 w-4 text-cyan-400" />

                {t("responseCards.evidence")}

              </CardTitle>

            </CardHeader>

            <CardContent className="space-y-3">

              {result.evidence.map((item, index) => {

                const sourceUrl = (item.metadata?.source_url as string | undefined) ?? null;

                return (

                  <motion.div

                    key={`${item.chunk_id}-${index}`}

                    initial={{ opacity: 0, y: 6 }}

                    animate={{ opacity: 1, y: 0 }}

                    transition={{ delay: index * 0.05 }}

                    className="rounded-xl border border-border/40 bg-muted/10 p-4"

                  >

                    <p className={cn("text-sm leading-relaxed", isArabic && "font-arabic")}>{item.text}</p>

                    <p className="mt-3 text-xs text-muted-foreground">

                      {item.source_author}

                      {item.source_title && item.source_title !== item.source_author && ` · ${item.source_title}`}

                    </p>

                    <p className="mt-2">
                      {t("explainability.citation")}:{" "}
                      <CitationLink
                        citation={item.citation}
                        url={sourceUrl}
                        sourceId={item.source_id}
                        sourceTitle={item.source_title}
                        sourceAuthor={item.source_author}
                        snippet={item.text}
                        onOpenSource={openSourcePanel}
                      />
                    </p>

                  </motion.div>

                );

              })}

            </CardContent>

          </Card>

        </RevealSection>

      )}



      {(result.principles.length > 0 || reasoningText) && (

        <RevealSection visible={!revealProgressively || isVisible("analysis")}>

          <Card className="glass-card border-violet-500/20">

            <CardHeader className="pb-2">

              <CardTitle className="text-sm font-semibold text-violet-300">{t("responseCards.analysis")}</CardTitle>

            </CardHeader>

            <CardContent className="space-y-4">

              {result.principles.length > 0 && (

                <div className="space-y-2">

                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">

                    {t("explainability.principles")}

                  </p>

                  {result.principles.map((principle) => (

                    <div key={principle.name} className="rounded-lg border border-border/40 p-3">

                      <p className={cn("font-medium", isArabic && "font-arabic")}>{principle.name}</p>

                      <p className={cn("mt-1 text-sm text-muted-foreground", isArabic && "font-arabic")}>

                        {principle.description}

                      </p>

                      <p className="mt-2 text-xs text-primary">{principle.citation}</p>

                    </div>

                  ))}

                </div>

              )}

              {reasoningText && (

                <div>

                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">

                    {t("explainability.reasoning")}

                  </p>

                  <p className={cn("whitespace-pre-wrap text-sm leading-relaxed", isArabic && "font-arabic")}>

                    {reasoningText}

                  </p>

                </div>

              )}

            </CardContent>

          </Card>

        </RevealSection>

      )}



      {result.opinions.length > 0 && (

        <RevealSection visible={!revealProgressively || isVisible("opinions")}>

          <Card className="glass-card border-border/50">

            <CardHeader className="pb-2">

              <CardTitle className="text-sm font-semibold">{t("responseCards.opinions")}</CardTitle>

            </CardHeader>

            <CardContent className="overflow-x-auto">

              <table className="w-full min-w-[560px] text-left text-sm">

                <thead>

                  <tr className="border-b border-border/50 text-xs text-muted-foreground">

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colScholar")}</th>

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colInstitution")}</th>

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colOpinion")}</th>

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colStrength")}</th>

                    <th className="pb-2 font-medium">{t("responseCards.colSource")}</th>

                  </tr>

                </thead>

                <tbody>

                  {result.opinions.map((opinion) => {
                    const metaParts = [
                      opinion.book ? `${t("responseCards.colBook")}: ${opinion.book}` : null,
                      opinion.fatwa ? `${t("responseCards.colFatwa")}: ${opinion.fatwa}` : null,
                      opinion.page ? `${t("responseCards.colPage")}: ${opinion.page}` : null,
                      opinion.standard ? `${t("responseCards.colStandard")}: ${opinion.standard}` : null,
                      opinion.section ? `${t("responseCards.colSection")}: ${opinion.section}` : null,
                      opinion.date ? `${t("responseCards.colDate")}: ${opinion.date}` : null,
                    ].filter(Boolean);

                    return (
                    <tr key={`${opinion.scholar}-${opinion.position.slice(0, 24)}`} className="border-b border-border/30">
                      <td className="py-3 pe-3 align-top font-medium text-violet-300">{opinion.scholar}</td>
                      <td className="py-3 pe-3 align-top text-xs text-muted-foreground">
                        {opinion.institution || "—"}
                      </td>
                      <td className={cn("py-3 pe-3 align-top", isArabic && "font-arabic")}>
                        <p>{opinion.position}</p>
                        {metaParts.length > 0 && (
                          <p className="mt-1 text-xs text-muted-foreground">{metaParts.join(" · ")}</p>
                        )}
                      </td>
                      <td className="py-3 pe-3 align-top text-xs">{opinion.strength || "—"}</td>
                      <td className="py-3 align-top text-xs text-muted-foreground">
                        {opinion.citations.join(" · ") || "—"}
                      </td>
                    </tr>
                    );
                  })}

                </tbody>

              </table>

            </CardContent>

          </Card>

        </RevealSection>

      )}



      {madhhabMatrix.length > 0 && (

        <RevealSection visible={!revealProgressively || isVisible("madhhab")}>

          <Card className="glass-card border-indigo-500/20">

            <CardHeader className="pb-2">

              <CardTitle className="flex items-center gap-2 text-sm font-semibold text-indigo-300">

                <Scale className="h-4 w-4" />

                {t("responseCards.madhhabMatrix")}

              </CardTitle>

            </CardHeader>

            <CardContent className="overflow-x-auto">

              <table className="w-full min-w-[520px] text-left text-sm">

                <thead>

                  <tr className="border-b border-border/50 text-xs text-muted-foreground">

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colSchool")}</th>

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colPosition")}</th>

                    <th className="pb-2 pe-3 font-medium">{t("responseCards.colAlignment")}</th>

                    <th className="pb-2 font-medium">{t("responseCards.colSource")}</th>

                  </tr>

                </thead>

                <tbody>

                  {madhhabMatrix.map((row) => (

                    <tr key={`${row.school}-${row.position.slice(0, 20)}`} className="border-b border-border/30">

                      <td className="py-3 pe-3 align-top font-medium">{row.school}</td>

                      <td className={cn("py-3 pe-3 align-top", isArabic && "font-arabic")}>{row.position}</td>

                      <td className="py-3 pe-3 align-top">

                        <Badge

                          variant="outline"

                          className={cn("text-[10px] capitalize", ALIGNMENT_STYLES[row.alignment] ?? ALIGNMENT_STYLES.mixed)}

                        >

                          {alignmentLabel(row.alignment)}

                        </Badge>

                      </td>

                      <td className="py-3 align-top text-xs text-muted-foreground">{row.source || "—"}</td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </CardContent>

          </Card>

        </RevealSection>

      )}



      {hasFinancial && financial && (

        <RevealSection visible={!revealProgressively || isVisible("financial")}>

          <Card className="glass-card border-teal-500/20">

            <CardHeader className="pb-2">

              <CardTitle className="flex items-center gap-2 text-sm font-semibold text-teal-300">

                <LineChart className="h-4 w-4" />

                {t("responseCards.financialAnalysis")}

              </CardTitle>

            </CardHeader>

            <CardContent className="space-y-4">

              {financial.entities.length > 0 && (

                <div>

                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">

                    {t("responseCards.entities")}

                  </p>

                  <div className="flex flex-wrap gap-2">

                    {financial.entities.map((entity) => (

                      <Badge key={entity} variant="secondary">

                        {entity}

                      </Badge>

                    ))}

                  </div>

                </div>

              )}



              {(financial.market_quotes?.length ?? 0) > 0 && (

                <div className="overflow-x-auto">

                  <table className="w-full min-w-[420px] text-left text-sm">

                    <thead>

                      <tr className="border-b border-border/50 text-xs text-muted-foreground">

                        <th className="pb-2 pe-3 font-medium">{t("responseCards.colSymbol")}</th>

                        <th className="pb-2 pe-3 font-medium">{t("responseCards.colPrice")}</th>

                        <th className="pb-2 font-medium">{t("responseCards.colExchange")}</th>

                      </tr>

                    </thead>

                    <tbody>

                      {financial.market_quotes?.map((quote) => (

                        <tr key={quote.symbol} className="border-b border-border/30">

                          <td className="py-2 pe-3 font-medium">{quote.symbol}</td>

                          <td className="py-2 pe-3">

                            {quote.price != null

                              ? `${quote.price.toLocaleString()} ${quote.currency ?? ""}`.trim()

                              : "—"}

                          </td>

                          <td className="py-2 text-xs text-muted-foreground">{quote.exchange || "—"}</td>

                        </tr>

                      ))}

                    </tbody>

                  </table>

                </div>

              )}



              {(financial.screening_notes?.length ?? 0) > 0 && (

                <div>

                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">

                    {t("responseCards.screeningNotes")}

                  </p>

                  <ul className="space-y-2 text-sm">

                    {financial.screening_notes?.map((note) => (

                      <li key={note} className="rounded-lg border border-border/40 bg-muted/10 px-3 py-2">

                        {note}

                      </li>

                    ))}

                  </ul>

                </div>

              )}



              {financial.notes && (

                <p className="text-sm text-muted-foreground">{financial.notes}</p>

              )}

            </CardContent>

          </Card>

        </RevealSection>

      )}



      {result.sources.length > 0 && (

        <RevealSection visible={!revealProgressively || isVisible("sources")}>

          <Card className="glass-card border-border/50">

            <CardHeader className="pb-2">

              <CardTitle className="text-sm font-semibold">{t("responseCards.sources")}</CardTitle>

            </CardHeader>

            <CardContent>
              <SourceCardsSection
                result={result}
                openSourceIds={openSourceIds}
                onOpenSource={openSourcePanel}
                onOpenSourceIdsChange={setOpenSourceIds}
              />
            </CardContent>

          </Card>

        </RevealSection>

      )}

    </div>

  );

});


