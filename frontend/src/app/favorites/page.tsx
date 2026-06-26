import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { FavoritesPanel } from "@/features/library/components/LibraryPanels";
import { PageLayout } from "@/components/PageGuide";

export const dynamic = "force-dynamic";

export default function FavoritesPage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="favorites" className="page-shell">
        <FavoritesPanel />
      </PageLayout>
    </AuthGuard>
  );
}
