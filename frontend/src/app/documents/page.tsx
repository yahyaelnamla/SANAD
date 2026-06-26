import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { DocumentAnalyzerPanel } from "@/features/documents/components/DocumentAnalyzerPanel";
import { PageLayout } from "@/components/PageGuide";

export const dynamic = "force-dynamic";

export default function DocumentsPage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="documents" className="page-shell">
        <DocumentAnalyzerPanel />
      </PageLayout>
    </AuthGuard>
  );
}
