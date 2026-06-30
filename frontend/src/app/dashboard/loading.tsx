export default function DashboardLoading() {
  return (
    <div className="container py-8 space-y-6">
      <div className="space-y-2">
        <div className="h-8 w-64 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
        <div className="h-4 w-96 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      </div>
      <div className="w-full h-12 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      <div className="border border-neutral-200 dark:border-neutral-800 rounded-lg p-6 h-[400px] flex items-center justify-center">
        <div className="w-full h-full bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="border border-neutral-200 dark:border-neutral-800 rounded-lg p-6 space-y-3">
            <div className="h-4 w-24 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
            <div className="h-8 w-32 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
            <div className="h-3 w-40 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
