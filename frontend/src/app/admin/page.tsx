import nextDynamic from "next/dynamic";

import { AdminGuard } from "@/features/admin/components/AdminGuard";
import { PageLoader } from "@/components/PageLoader";

const AdminDashboard = nextDynamic(
  () => import("@/features/admin/components/AdminDashboard").then((mod) => mod.AdminDashboard),
  { loading: () => <PageLoader /> },
);

export const dynamic = "force-dynamic";

export default function AdminPage() {
  return (
    <AdminGuard>
      <AdminDashboard />
    </AdminGuard>
  );
}
