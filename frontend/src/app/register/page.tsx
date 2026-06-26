import { RegisterForm } from "@/features/auth/components/RegisterForm";
import { RedirectIfAuthenticated } from "@/features/auth/components/RedirectIfAuthenticated";

export default function RegisterPage() {
  return (
    <RedirectIfAuthenticated>
      <RegisterForm />
    </RedirectIfAuthenticated>
  );
}
