export default function CalculatorLoading() {
  return (
    <div className="container py-8 max-w-2xl mx-auto space-y-6">
      <div className="h-8 w-48 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      <div className="w-full h-12 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      <div className="border border-neutral-200 dark:border-neutral-800 rounded-lg p-6 space-y-6">
        <div className="space-y-2">
          <div className="h-6 w-32 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
          <div className="h-4 w-64 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
        </div>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-2">
              <div className="h-4 w-20 bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
              <div className="h-10 w-full bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
            </div>
          ))}
        </div>
        <div className="h-10 w-full bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded" />
      </div>
    </div>
  );
}
