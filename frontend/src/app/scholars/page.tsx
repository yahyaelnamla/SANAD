import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { ScholarBrowsePanel } from "@/features/scholars/components/ScholarBrowsePanel";

export default function ScholarsPage() {
  return (
    <AuthGuard>
      <div className="page-shell">
        <ScholarBrowsePanel />
      </div>
    </AuthGuard>
  );
}
