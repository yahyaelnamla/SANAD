"use client";

import { ArrowLeft, BookOpen, GraduationCap, Loader2 } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { scholarDisplayName } from "@/lib/scholarDisplay";
import {
  localizeExpertiseTag,
  localizeGraphNodeType,
  localizeScholarInstitution,
} from "@/lib/domainLocalizations";
import { ApiClientError } from "@/services/apiClient";
import { getScholar, type ScholarProfile } from "@/services/scholarService";

interface ScholarProfilePanelProps {
  slug: string;
}

export function ScholarProfilePanel({ slug }: ScholarProfilePanelProps) {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const [profile, setProfile] = useState<ScholarProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!accessToken) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setProfile(await getScholar(accessToken, slug));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  }, [accessToken, slug, locale]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="mx-auto max-w-2xl space-y-4 text-center">
        <p className="text-destructive">{error ?? t("scholars.notFound")}</p>
        <Button variant="outline" asChild>
          <Link href="/scholars">{t("scholars.backToList")}</Link>
        </Button>
      </div>
    );
  }

  const names = scholarDisplayName(profile, locale);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Button variant="ghost" size="sm" className="gap-1" asChild>
        <Link href="/scholars">
          <ArrowLeft className="h-4 w-4" />
          {t("scholars.backToList")}
        </Link>
      </Button>

      <Card className="glass-card border-cyan-500/20">
        <CardHeader>
          <CardTitle className="flex flex-col gap-1 text-xl">
            <span className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-cyan-400" />
              {names.primary}
            </span>
            {names.secondary && (
              <span className="text-sm font-normal text-muted-foreground">{names.secondary}</span>
            )}
          </CardTitle>
          {profile.institution && (
            <p className="text-sm text-muted-foreground">
              {localizeScholarInstitution(profile.slug, profile.institution, locale)}
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {(locale === "ar" ? profile.bio_ar ?? profile.bio : profile.bio) && (
            <p className="text-sm leading-relaxed">
              {locale === "ar" ? profile.bio_ar ?? profile.bio : profile.bio}
            </p>
          )}
          <div className="flex flex-wrap gap-1">
            {profile.expertise.map((tag) => (
              <Badge key={tag} variant="outline">
                {localizeExpertiseTag(tag, locale)}
              </Badge>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            {profile.source_count} {t("scholars.sourcesLabel")}
          </p>
        </CardContent>
      </Card>

      {profile.sources.length > 0 && (
        <Card className="glass-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold">{t("scholars.relatedSources")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {profile.sources.map((source) => (
              <div
                key={source.id}
                className="flex items-start gap-2 rounded-lg border border-border/40 bg-muted/10 p-3"
              >
                <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-cyan-400" />
                <div>
                  <p className="text-sm font-medium">{source.title}</p>
                  <Badge variant="secondary" className="mt-1 text-[10px]">
                    {localizeGraphNodeType(source.source_type, locale)}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {profile.opinion_samples.length > 0 && (
        <Card className="glass-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold">{t("scholars.opinionSamples")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.opinion_samples.map((sample, index) => (
              <div key={index} className="rounded-lg border border-border/40 p-3">
                <p className="text-sm leading-relaxed">{sample.position}</p>
                {sample.date && (
                  <p className="mt-1 text-xs text-muted-foreground">{sample.date}</p>
                )}
                {sample.citations.length > 0 && (
                  <p className="mt-2 text-xs text-primary">{sample.citations.join(" · ")}</p>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
