import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { BookmarksPanel } from "@/features/library/components/LibraryPanels";
import { PageLayout } from "@/components/PageGuide";

export const dynamic = "force-dynamic";

export default function BookmarksPage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="bookmarks" className="page-shell">
        <BookmarksPanel />
      </PageLayout>
    </AuthGuard>
  );
}
