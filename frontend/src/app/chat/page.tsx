import { Suspense } from "react";

import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { ChatPageSkeleton } from "@/components/ChatPageSkeleton";
import { ChatInterface } from "@/features/chat/components/ChatInterface";

export const dynamic = "force-dynamic";

export default function ChatPage() {
  return (
    <AuthGuard variant="chat">
      <div className="flex h-full min-h-0 flex-1 flex-col">
        <Suspense fallback={<ChatPageSkeleton />}>
          <ChatInterface />
        </Suspense>
      </div>
    </AuthGuard>
  );
}
