import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { PortfolioScannerPanel } from "@/features/tools/components/PortfolioScannerPanel";

export const dynamic = "force-dynamic";

export default function PortfolioScannerPage() {
  return (
    <AuthGuard>
      <PortfolioScannerPanel />
    </AuthGuard>
  );
}
