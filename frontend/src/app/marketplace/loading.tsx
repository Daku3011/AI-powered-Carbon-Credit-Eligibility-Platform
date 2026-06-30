export default function MarketplaceLoading() {
  return (
    <div className="container py-8">
      <div className="mb-6 space-y-2">
        <div className="h-8 w-48 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
        <div className="h-4 w-96 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="border border-neutral-200 dark:border-neutral-800 rounded-lg p-6 space-y-4">
            <div className="flex justify-between items-start">
              <div className="h-6 w-32 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
              <div className="h-6 w-16 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded-full" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-full bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
              <div className="h-4 w-3/4 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
            </div>
            <div className="pt-4 border-t border-neutral-200 dark:border-neutral-800 grid grid-cols-2 gap-4">
              <div className="h-4 w-20 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
              <div className="h-4 w-16 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
              <div className="h-4 w-24 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
