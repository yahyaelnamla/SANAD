import nextDynamic from "next/dynamic";

import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { PageLayout } from "@/components/PageGuide";
import { PageLoader } from "@/components/PageLoader";

const KnowledgeGraphPanel = nextDynamic(
  () =>
    import("@/features/knowledge/components/KnowledgeGraphPanel").then((mod) => mod.KnowledgeGraphPanel),
  { loading: () => <PageLoader /> },
);

export const dynamic = "force-dynamic";

export default function KnowledgeGraphPage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="knowledgeGraph" className="page-shell">
        <KnowledgeGraphPanel />
      </PageLayout>
    </AuthGuard>
  );
}
