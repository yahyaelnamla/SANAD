"use client";

interface ChatPageSkeletonProps {
  withSidebar?: boolean;
}

export function ChatPageSkeleton({ withSidebar = false }: ChatPageSkeletonProps) {
  return (
    <div className="flex h-full min-h-0 w-full flex-col">
      <div className="glass-card flex min-h-0 flex-1 flex-col overflow-hidden">
        <div className="flex min-h-0 flex-1 flex-col items-center justify-center px-4 py-8">
          <div className="mb-3 h-12 w-12 rounded-2xl skeleton-block" />
          <div className="mb-2 h-5 w-44 rounded-md skeleton-block" />
          <div className="h-4 w-56 max-w-full rounded-md skeleton-block" />
        </div>
        <div className="shrink-0 border-t border-border/50 p-3">
          <div className="mb-2 h-8 w-48 rounded-lg skeleton-block" />
          <div className="h-16 w-full rounded-xl skeleton-block" />
        </div>
      </div>
      {withSidebar && <span className="sr-only">Loading sidebar</span>}
    </div>
  );
}
