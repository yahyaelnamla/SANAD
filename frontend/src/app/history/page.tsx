import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { HistoryList } from "@/features/history/components/HistoryList";
import { HistoryPageTitle } from "@/features/history/components/HistoryPageTitle";

export const dynamic = "force-dynamic";

export default function HistoryPage() {
  return (
    <AuthGuard>
      <div className="space-y-6">
        <HistoryPageTitle />
        <HistoryList />
      </div>
    </AuthGuard>
  );
}
