import { LoginForm } from "@/features/auth/components/LoginForm";
import { RedirectIfAuthenticated } from "@/features/auth/components/RedirectIfAuthenticated";

export default function LoginPage() {
  return (
    <RedirectIfAuthenticated>
      <LoginForm />
    </RedirectIfAuthenticated>
  );
}
