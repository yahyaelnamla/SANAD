import { RedirectIfAuthenticated } from "@/features/auth/components/RedirectIfAuthenticated";
import { LandingPage } from "@/features/marketing/components/LandingPage";

export default function WelcomePage() {
  return (
    <RedirectIfAuthenticated>
      <LandingPage />
    </RedirectIfAuthenticated>
  );
}
