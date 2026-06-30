export default function ChatbotLoading() {
  return (
    <div className="container py-8 max-w-3xl mx-auto space-y-6">
      <div className="space-y-2">
        <div className="h-8 w-48 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
        <div className="h-4 w-96 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      </div>
      <div className="border border-neutral-200 dark:border-neutral-800 rounded-lg p-6 h-[400px] flex flex-col justify-between">
        <div className="space-y-4">
          <div className="h-10 w-2/3 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
          <div className="h-10 w-1/2 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded ml-auto" />
        </div>
        <div className="h-12 w-full bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      </div>
    </div>
  );
}
