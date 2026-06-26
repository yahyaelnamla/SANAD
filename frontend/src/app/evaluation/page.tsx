"use client";

import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { FanarJudgeDashboard } from "@/features/evaluation/components/FanarJudgeDashboard";
import { PageLayout } from "@/components/PageGuide";

export default function EvaluationPage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="evaluation" className="page-shell">
        <FanarJudgeDashboard />
      </PageLayout>
    </AuthGuard>
  );
}