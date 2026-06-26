import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { KnowledgeBrowsePanel } from "@/features/knowledge/components/KnowledgeBrowsePanel";
import { PageLayout } from "@/components/PageGuide";

export const dynamic = "force-dynamic";

export default function KnowledgePage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="knowledge" className="page-shell">
        <KnowledgeBrowsePanel />
      </PageLayout>
    </AuthGuard>
  );
}
