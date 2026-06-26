import { OnboardingGuard } from "@/features/auth/components/OnboardingGuard";
import { OnboardingWizard } from "@/features/onboarding/components/OnboardingWizard";

export default function OnboardingPage() {
  return (
    <OnboardingGuard>
      <OnboardingWizard />
    </OnboardingGuard>
  );
}
