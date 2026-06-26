import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { ZakatCalculatorPanel } from "@/features/tools/components/ZakatCalculatorPanel";
import { PageLayout } from "@/components/PageGuide";

export const dynamic = "force-dynamic";

export default function ZakatPage() {
  return (
    <AuthGuard>
      <PageLayout guideKey="zakat" className="page-shell">
        <ZakatCalculatorPanel />
      </PageLayout>
    </AuthGuard>
  );
}
