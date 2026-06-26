import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { ScholarProfilePanel } from "@/features/scholars/components/ScholarProfilePanel";

interface ScholarDetailPageProps {
  params: { slug: string };
}

export default function ScholarDetailPage({ params }: ScholarDetailPageProps) {
  return (
    <AuthGuard>
      <div className="page-shell">
        <ScholarProfilePanel slug={params.slug} />
      </div>
    </AuthGuard>
  );
}
