import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { CompanyScannerPanel } from "@/features/tools/components/CompanyScannerPanel";

export const dynamic = "force-dynamic";

export default function CompanyScannerPage() {
  return (
    <AuthGuard>
      <CompanyScannerPanel />
    </AuthGuard>
  );
}
